# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from collections import defaultdict

from ._utils import ask
from ._zotero import connect


def merge_duplicate_tags(library=None):
    "Merge tags that differ only in capitalization"
    z = connect(library)

    print("Retrieving Library...")
    items = z.everything(z.top())

    tags = collect_tags(items)
    mod = find_duplicates(tags)
    updated = update_tags(mod, items)

    if updated:
        print("Updating library...")
        for i in updated:
            z.update_item(items[i])
    else:
        print("No items found.")


def collect_tags(items):
    "Return a set of all tags"
    out = set()
    for item in items:
        out.update((i['tag'] for i in item['data']['tags']))
    return out


def find_duplicates(tags):
    equal = defaultdict(set)
    for tag in tags:
        equal[tag.lower()].add(tag)

    conflicts = {key: list(versions) for key, versions in equal.iteritems() if
                 len(versions) > 1}

    modifications = {}
    # ask user what to do
    for key, versions in conflicts.iteritems():
        # acronyms
        upper = versions[0].upper()
        capitalized = versions[0].capitalize()
        for ideal in (upper, capitalized):
            if any(v == ideal for v in versions):
                modifications.update({v: ideal for v in versions if v != ideal})
                break
        else:
            versions.append(capitalized)
            print('\n'.join("%i: %s" % item for item in enumerate(versions, 1)))
            options = [str(i) for i in xrange(1, len(versions) + 1)] + ['s']
            cmd = ask("# to keep (or [s]kip)", options)
            if cmd != 's':
                target = versions[int(cmd) - 1]
                for v in versions:
                    if v != target:
                        modifications[v] = target
    return modifications


def remove_stars(library=None):
    z = connect(library)
    print("Retrieving Library...")
    items = z.everything(z.top())
    changed_items = set()

    for item_i, item in enumerate(items):
        tags = item['data']['tags']
        labels = [t['tag'] for t in tags]
        for i in xrange(len(tags)-1, -1, -1):
            label = tags[i]['tag']
            if label.startswith('*'):
                new = label[1:]
                if new in labels:
                    print("rm " + label)
                    del tags[i]
                else:
                    print(label + ' -> ' + new)
                    tags[i]['tag'] = new
                changed_items.add(item_i)

    # ask for confirmation/apply
    if ask("Apply changes?") == 'y':
        print("Updating library...")
        for i in changed_items:
            z.update_item(items[i])


def update_tags(modifications, items):
    "Apply {old: new} modifications"
    updated_items = set()

    for item_i, item in enumerate(items):
        tags = [i['tag'] for i in item['data']['tags']]
        for i, tag in reversed(list(enumerate(tags))):
            if tag in modifications:
                new = modifications[tag]
                if new in tags:
                    del item['data']['tags'][i]
                else:
                    item['data']['tags'][i] = {u'tag': new}
                updated_items.add(item_i)
    return updated_items
