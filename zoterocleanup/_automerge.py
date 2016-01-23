# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from collections import defaultdict

from ._zotero import connect, date_added


def auto_merge(library=None):
    """Merge duplicate items

    Parameters
    ----------
    library : str | int
        Library ID.

    Notes
    -----
    Find duplicate items by DOI and ISBN. For each identifier, Keep only the
    oldest item, but use the attachments from the newest item that has
    attachments.
    """
    z = connect(library)

    print("Retrieving Library...")
    items = z.everything(z.top())

    print("Resolving duplicates...")
    # sort items by DOI
    by_doi = defaultdict(list)
    for item in items:
        if 'DOI' in item['data']:
            by_doi[item['data']['DOI']].append(item)
        elif 'ISBN' in item['data']:
            by_doi[item['data']['ISBN']].append(item)

    delete = []
    update = []
    for doi, items in by_doi.iteritems():
        if len(items) == 1:
            continue

        # sort by age
        items.sort(key=date_added)

        # keep oldest item
        keep = items[0]

        # keep latest attachments
        keep_cs = z.children(keep['key'])
        for item in items[-1:0:-1]:
            cs = z.children(item['key'])
            if cs:
                for c in cs:
                    c['data']['parentItem'] = keep['key']
                update.extend(cs)
                delete.extend(keep_cs)
                break

        delete.extend(items[1:])

    print("Updating library...")
    # update first, so we don't delete parents of items we want to keep
    for item in update:
        z.update_item(item)
    for item in delete:
        z.delete_item(item)
