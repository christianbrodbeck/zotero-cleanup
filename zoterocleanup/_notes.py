import re

from bs4 import BeautifulSoup

from ._utils import ask
from ._zotero import connect


AUTO_TOC_START = '<p(?: id="title")?><strong>Contents</strong></p>'


def remove_notes(verbose=True, pattern=AUTO_TOC_START):
    """Remove notes matching a pattern
    
    Parameters
    ----------
    verbose : bool
        Print all the notes that would be removed.
    pattern : str
        The pattern that notes are matched with (the default is 
        ``"<p><strong>Contents</strong></p>"``, the beginning of automatically
        generated table of contents).
    """
    if pattern is None:
        pattern = AUTO_TOC_START
    z = connect()
    print("Retrieving Library...")
    items = z.everything(z.top())
    print("Scanning children for notes...")
    changed_items = []
    for item in items:
        children = z.children(item['key'])
        for child in children:
            if re.match(pattern, child['data']['note']):
                if verbose:
                    title = child['data']['title'][:80]
                    print(title)
                    print('-' * len(title))
                    soup = BeautifulSoup(child['data']['note'], "lxml")
                    print(soup.get_text() + '\n')
                child['data']['note'] = ''
                changed_items.append(child)

    if not changed_items:
        print("No notes with auto TOC found")
        return
    print("%i notes found. Should they be deleted?" % len(changed_items))
    if ask("Proceed?") == 'y':
        print("Updating library...")
        for item in changed_items:
            z.update_item(item)
