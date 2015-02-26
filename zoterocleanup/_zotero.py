# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import sys

import keyring
from pyzotero import zotero

BUFFER_SIZE = 25
KEYRING_DOMAIN = "Zotero Cleanup Library"


def connect():
    user = raw_input("Library ID: ")
    password = keyring.get_password(KEYRING_DOMAIN, user)
    if password is None:
        password = raw_input("Library Password: ")
        if password:
            keyring.set_password(KEYRING_DOMAIN, user, password)
        else:
            sys.exit()
    return zotero.Zotero(user, 'user', password, True)

z = connect()


def get_items():
    print "Retrieving items from Zotero server..."
    num_items = z.num_items()
    items = []
    for buffer_i in xrange(0, num_items, BUFFER_SIZE):
        item_buffer = z.top(start=buffer_i, limit=BUFFER_SIZE)
        items.extend(item_buffer)
    if len(items) != num_items:
        raise RuntimeError("Not all items retrieved")
    return items


def update_items(items):
    print "Updating items...",
    for item in items:
        z.update_item(item)
