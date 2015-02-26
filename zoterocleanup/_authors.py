# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from ._zotero import get_items, update_items


def rename_author(last, first, newlast=None, newfirst=None):
    """Rename a single author

    Parameters
    ----------
    last : str
        Author's last name.
    first : str
        Author's given name(s).
    newlast : str (optional)
        New entry for author's last name.
    newfirst : str (optional)
        New entry for author's given name(s).
    """
    if newlast is None and newfirst is None:
        raise ValueError("Need to change at least one component")
    elif newlast is None:
        print "%s, %s -> %s, %s" % (last, first, last, newfirst)
    elif newfirst is None:
        print "%s, %s -> %s, %s" % (last, first, newlast, first)
    else:
        print "%s, %s -> %s, %s" % (last, first, newlast, newfirst)

    items = get_items()
    changed_items = []
    for i, item in enumerate(items):
        for person in item['data']['creators']:
            if person['lastName'] == last and person['firstName'] == first:
                if newlast is not None:
                    person['lastName'] = newlast
                if newfirst is not None:
                    person['firstName'] = newfirst
                changed_items.append(item)

    if raw_input("Change %i occurrences [yes/no]? " % len(changed_items)) == 'yes':
        update_items(changed_items)
    else:
        print "Aborted"
