# zotero-cleanup

Maintenance of a Zotero library based on 
[pyzotero](http://pyzotero.readthedocs.io).

Installs the script:

    $ zoterocleanup

These functions modify the library hosted on [zotero.org](http://zotero.org). 
Keep a local backup of your library!


## Normalizing author names

If the same author has entries with different spellings in a library 
(e.g., "Albert Einstein" vs. "A Einstein") this can lead to errors in
bibliographies with standards for disambiguating authors with similar names.
This function scans the library for alternate spellings of the same author and
changes them to a unified version:

	$ zoterocleanup merge-authors

A list of all changes is printed for confirmation before applying any changes.
