# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import re
import urllib
from ._zotero import connect


REQUEST = ('http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/'
           '?tool=zoterocleanup&email=christianbrodbeck@nyu.edu&ids=')


def find_doi(source, identifier):
    if source == 'PMID' or source == 'DOI':
        request = REQUEST + str(identifier)
    elif source == 'PMCID':
        request = REQUEST + 'PMC' + str(identifier)
    elif source == 'NIHMS':
        request = REQUEST + 'NIHMS' + str(identifier)
    else:
        raise ValueError("Unknown source: %r" % source)
    txt = urllib.urlopen(request).read()
    m = re.match('doi="([0-9a-zA-Z/.]+)"', txt)
    if m:
        return m.group(1)
    # else:
    #     print "No DOI returned in:" + txt


def check_for_missing_dois(library=None):
    z = connect(library)
    print("Retrieving Library...")
    items = z.everything(z.top())

    print("Items missing DOI:")
    changed = []
    for i, item in enumerate(items):
        if not item['data'].get('DOI'):
            if 'extra' in item['data']:
                m = re.match("PMID: (\d+)", item['data']['extra'])
            else:
                m = None

            if m:
                pmid = m.group(1)
                doi = find_doi('PMID', pmid)
                if doi:
                    item['data']['DOI'] = doi
                    print("%s -> %s" % (item['data']['key'], doi))
                    changed.append(i)
                else:
                    m = None

            if m is None:
                print(item['data']['key'])
