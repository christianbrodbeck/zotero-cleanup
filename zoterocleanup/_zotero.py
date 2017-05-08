# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from configparser import SafeConfigParser
from datetime import datetime
from os.path import exists, expanduser, join

import keyring
from pyzotero.zotero import Zotero
from pyzotero.zotero_errors import UserNotAuthorised

DATE_FMT = "%Y-%m-%dT%XZ"
KEYRING_DOMAIN = "Zotero Cleanup Library"
CONFIG_PATH = join(expanduser('~'), '.zotero_cleanup.cfg')


def connect(library=None, api_key=None):
    config_library = get_library()
    if library is None:
        library = config_library
    else:
        library = str(library)
    # user input
    if library is None:
        while True:
            library = raw_input("Library ID: ")
            if library and library.isdigit():
                break
            print("Library needs to be a sequence of digits, not %r" % library)

    if api_key is None:
        api_key = keyring.get_password(KEYRING_DOMAIN, library)
        api_key_changed = False
    else:
        api_key_changed = True

    msg_printed = False
    while True:
        if not api_key:
            if not msg_printed:
                print("Please enter the library API key "
                      "(see https://www.zotero.org/settings/keys/new)")
                msg_printed = True
            api_key = raw_input("Library API key (ctrl-c to abort): ")

        z = Zotero(library, 'user', api_key, True)
        try:
            z.num_items()
        except UserNotAuthorised:
            print("Connection refused, invalid API key...")
            api_key = None
        else:
            # store new configuration
            if library != config_library:
                set_library(library)
            if api_key_changed:
                keyring.set_password(KEYRING_DOMAIN, library, api_key)
            return z


def date_added(item):
    return datetime.strptime(item['data']['dateAdded'], DATE_FMT)


def get_library():
    config = SafeConfigParser()
    if exists(CONFIG_PATH):
        config.read(CONFIG_PATH)
        return config.get('library', 'id')


def set_library(library):
    config = SafeConfigParser()
    config.add_section('library')
    config.set('library', 'id', library)
    config.write(open(CONFIG_PATH, 'w'))
