# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from collections import defaultdict
from itertools import izip_longest
import re

from ._utils import ask
from ._zotero import connect

PREFIXES = ('van', 'von', 'de')


class Given(object):

    def __init__(self, names):
        names_ = []
        for name in names:  # can't just capitalize ("DuBois")
            if name[0].islower():
                name = name[0].capitalize() + name[1:]
            names_.append(name)
        self.names = tuple(names_)
        self.namestring = ' '.join(self.names)

    @classmethod
    def from_namestring(cls, namestring):
        return cls(re.findall(u"([\w-]+).?\s*", namestring, re.UNICODE))

    def __eq__(self, other):
        return self.names == other.names

    def __hash__(self):
        return hash(self.namestring)

    def is_more_complete_than(self, other):
        if self == other:
            return False
        elif len(self.names) < len(other.names):
            return False

        for sname, oname in izip_longest(self.names, other.names, fillvalue=''):
            if not sname.startswith(oname):
                return False
        return True

    def should_merge(self, other):
        if self == other:
            return False

        for sname, oname in izip_longest(self.names, other.names, fillvalue=''):
            if not sname.startswith(oname) or oname.startswith(sname):
                return False

        return True

    def union(self, other):
        out = []
        for sname, oname in izip_longest(self.names, other.names, fillvalue=''):
            if len(sname) > len(oname):
                if sname.startswith(oname):
                    out.append(sname)
                else:
                    raise ValueError("can't merge %s and %s" % (sname, oname))
            elif oname.startswith(sname):
                out.append(oname)
            else:
                raise ValueError("can't merge %s and %s" % (sname, oname))
        return Given(out)


def merge_authors(library=None):
    """Find and merge different variations of author names

    Parameters
    ----------
    library : str | int
        Library ID.

    Notes
    -----
    Asks for confirmation Before applying any changes. The following operations
    are performed:

     - If a name is stored as single string, decompose it into first and last
       name
     - Fix names where part of the last name was assigned to the first name
       (e.g., "van" in "van Gogh")
     - Find missing middle initials.
    """
    z = connect(library)
    print("Retrieving Library...")
    items = z.everything(z.top())

    # filter out ones wthout authors
    items = [i for i in items if 'creators' in i['data']]

    print("Resolving author names...")
    changed_items = set()

    # decompose full names
    decomposed = {}  # full -> first, last
    ignored = set()
    for i, item in enumerate(items):
        for person in item['data']['creators']:
            if 'name' in person:
                if 'firstName' in person or 'lastName' in person:
                    raise RuntimeError("name and firstName or lastName")
                name = person.pop('name')
                if name in decomposed:
                    last, first = decomposed[name]
                else:
                    if name.count(',') == 1:
                        last, first = map(unicode.strip, name.split(','))
                    elif name.count(' ') == 1 and name.count(',') == 0:
                        first, last = map(unicode.strip, name.split(' '))
                    else:
                        m = re.match("(\w+ \w.?) (\w+)", name, re.UNICODE)
                        if m:
                            first, last = m.groups()
                        else:
                            ignored.add(name)
                            continue
                    decomposed[name] = (last, first)
                person['firstName'] = first
                person['lastName'] = last
                changed_items.add(i)

    # fix decomposition
    re_decomposed = {}  # {(first, last): (first, last)}
    for i, item in enumerate(items):
        for person in item['data']['creators']:
            if 'name' in person:
                continue
            first = person['firstName']
            last = person['lastName']
            for prefix in PREFIXES:
                if first.lower().endswith(' %s' % prefix):
                    n = len(prefix)
                    new_first = first[:-(n + 1)]
                    new_last = first[-n:] + ' ' + last
                    person['firstName'] = new_first
                    person['lastName'] = new_last
                    changed_items.add(i)
                    re_decomposed[(last, first)] = (new_last, new_first)

    # normalize and collect all names
    people = {}  # last -> set(firsts as Given)
    normalized = defaultdict(dict)  # {last: {first -> normalized_first}}
    for i, item in enumerate(items):
        for person in item['data']['creators']:
            if 'name' in person:
                continue
            first = person['firstName']
            last = person['lastName']
            first_g = Given.from_namestring(first)
            # normalize
            if first != first_g.namestring:
                person['firstName'] = first_g.namestring
                normalized[last][first] = first_g.namestring
                changed_items.add(i)
            # add to people
            if last in people:
                people[last].add(first_g)
            else:
                people[last] = {first_g}

    # find first names to merge
    merge = defaultdict(dict)  # {last: {first_src: first_dst}}
    for last, first_names in people.iteritems():
        if len(first_names) > 1:
            first_names = tuple(first_names)
            for i, first1 in enumerate(first_names, 1):
                for first2 in first_names[i:]:
                    if first1.is_more_complete_than(first2):
                        merge[last][first2.namestring] = first1.namestring
                    elif first2.is_more_complete_than(first1):
                        merge[last][first1.namestring] = first2.namestring
                    elif first1.should_merge(first2):
                        u = first1.union(first2)
                        merge[last][first1.namestring] = u.namestring
                        merge[last][first2.namestring] = u.namestring

    # apply first name merges
    for i, item in enumerate(items):
        for person in item['data']['creators']:
            if 'name' in person:
                continue
            last = person['lastName']
            if last not in merge:
                continue
            first = person['firstName']
            if first not in merge[last]:
                continue
            person['firstName'] = merge[last][first]
            changed_items.add(i)

    # print changes
    print "Decomposed:"
    for full in sorted(decomposed):
        last, first = decomposed[full]
        print "  %s -> %s, %s" % (full, last, first)
    print "Re-Decomposed:"
    for (l, f) in sorted(re_decomposed):
        nl, nf = re_decomposed[(l, f)]
        print "  %s, %s -> %s, %s" % (l, f, nl, nf)
    print "Remaining separate:"
    for last in sorted(people):
        first_names = people[last]
        remaining_first = []
        if len(first_names) > 1:
            mapping = merge.get(last, {})
            for first in first_names:
                if first.namestring not in mapping:
                    remaining_first.append(first.namestring)
        if len(remaining_first) > 1:
            print "  %s: %s" % (last, ', '.join(remaining_first))
    print "Normalized:"
    for last in sorted(normalized):
        mapping = normalized[last]
        print "  %s" % last
        for pair in mapping.iteritems():
            print "    %s -> %s" % pair
    print "To be merged:"
    for last in sorted(merge):
        print "  %s" % last
        for pair in merge[last].iteritems():
            print "    %s -> %s" % pair
    if ignored:
        print("Ignored author names:")
        for name in sorted(ignored):
            print("  %s" % name)

    # ask for confirmation/apply
    if ask("Apply changes?") == 'y':
        print("Updating library...")
        for i in changed_items:
            z.update_item(items[i])


def rename_author(last, first, newlast=None, newfirst=None, library=None):
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
    library : str | int
        Library ID.
    """
    if newlast is None and newfirst is None:
        raise ValueError("Need to change at least one component")
    elif newlast is None:
        print "%s, %s -> %s, %s" % (last, first, last, newfirst)
    elif newfirst is None:
        print "%s, %s -> %s, %s" % (last, first, newlast, first)
    else:
        print "%s, %s -> %s, %s" % (last, first, newlast, newfirst)

    z = connect(library)
    print("Retrieving Library...")
    items = z.everything(z.top())

    changed_items = []
    for i, item in enumerate(items):
        for person in item['data']['creators']:
            if person['lastName'] == last and person['firstName'] == first:
                if newlast is not None:
                    person['lastName'] = newlast
                if newfirst is not None:
                    person['firstName'] = newfirst
                changed_items.append(item)

    if ask("Change %i occurrences?" % len(changed_items)) == 'y':
        print("Updating library...")
        for item in changed_items:
            z.update_item(item)
