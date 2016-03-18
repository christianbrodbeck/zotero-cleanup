# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>

from ._authors import rename_author, merge_authors
from ._automerge import auto_merge
from ._dois import check_for_missing_dois
from ._tags import remove_stars, merge_duplicate_tags
from ._zotero import connect
