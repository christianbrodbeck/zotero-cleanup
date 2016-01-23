# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from datetime import datetime
import sys

import keyring
from pyzotero import zotero

DATE_FMT = "%Y-%m-%dT%XZ"
KEYRING_DOMAIN = "Zotero Cleanup Library"


def connect(library=None):
    if library is None:
        library = raw_input("Library ID: ")
    else:
        library = str(library)
    password = keyring.get_password(KEYRING_DOMAIN, library)
    if password is None:
        password = raw_input("Library Password: ")
        if password:
            keyring.set_password(KEYRING_DOMAIN, library, password)
        else:
            sys.exit()
    return zotero.Zotero(library, 'user', password, True)


def date_added(item):
    return datetime.strptime(item['data']['dateAdded'], DATE_FMT)
