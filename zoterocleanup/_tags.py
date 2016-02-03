# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from ._utils import ask
from ._zotero import connect


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
