#!/usr/bin/env python
from __future__ import division, print_function
import sys
from nexus import NexusReader, VERSION
from nexus.tools import count_site_values
from nexus.tools import check_zeros
from nexus.tools import find_constant_sites
from nexus.tools import find_unique_sites
from nexus.tools import new_nexus_without_sites
from nexus.bin.nexus_treemanip import parse_deltree

__author__ = 'Simon Greenhill <simon@simon.net.nz>'
__doc__ = """nexusmanip - python-nexus tools v%(version)s

Performs a number of nexus manipulation methods.
""" % {'version': VERSION, }


def print_site_values(nexus_obj, characters=None):
    """
    Prints out counts of the number of sites with state in `characters` in a
    nexus.

    (Wrapper around `count_site_values`)

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader
    """
    characters = characters if characters is not None else ['-', '?']
    
    count = count_site_values(nexus_obj, characters)
    print("Number of %s in %s" % (",".join(characters), nexus_obj.filename))
    for taxon in sorted(count):
        prop = (count[taxon] / nexus.data.nchar) * 100
        print(
            "%s: %d/%d (%0.2f%%)" %
            (taxon.ljust(20), count[taxon], nexus.data.nchar, prop)
        )
    print('-' * 76)
    total_count = sum([x for x in count.values()])
    total_data = nexus.data.nchar * nexus.data.ntaxa
    prop = (total_count / total_data) * 100
    print('TOTAL: %d/%d (%0.2f%%)' %
        (total_count, total_data, prop)
    )

def print_character_stats(nexus_obj):
    """
    Prints the number of states and members for each site in `nexus_obj`

    :param nexus_obj: A `NexusReader` instance
    :type nexus_obj: NexusReader

    :return: A list of the state distribution
    """
    state_distrib = []
    for i in range(0, nexus_obj.data.nchar):
        tally = {}
        for taxa, characters in nexus_obj.data:
            c = characters[i]
            tally[c] = tally.get(c, 0) + 1

        print("%5d" % i, end="")
        for state in tally:
            print("%sx%d" % (state, tally[state]), end="")
            state_distrib.append(tally[state])
        print("\n")
    return state_distrib




if __name__ == '__main__':
    #set up command-line options
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog old.nex [new.nex]")
    parser.add_option("-n", "--number", dest="number",
            action="store_true", default=False,
            help="Count the number of characters")
    parser.add_option("-c", "--constant", dest="constant",
            action="store_true", default=False,
            help="Remove the constant characters")
    parser.add_option("-u", "--unique", dest="unique",
            action="store_true", default=False,
            help="Remove the unique characters")
    parser.add_option("-x", "--remove", dest="remove",
            action="store", default=False,
            help="Remove the empty characters")
    parser.add_option("-z", "--zeros", dest="zeros",
            action="store_true", default=False,
            help="Remove the empty characters")
    parser.add_option("-s", "--stats", dest="stats",
            action="store_true", default=False,
            help="Print character-by-character stats")
    options, args = parser.parse_args()

    try:
        nexusname = args[0]
    except IndexError:
        print(__doc__)
        print("Author: %s\n" % __author__)
        parser.print_help()
        sys.exit()

    try:
        newnexusname = args[1]
    except IndexError:
        newnexusname = None


    nexus = NexusReader(nexusname)
    newnexus = None

    if options.number:
        print_site_values(nexus)
        exit()
    
    if options.stats:
        print_character_stats(nexus)
        exit()
        
    const, unique, zeros, remove = [], [], [], []
    if options.constant:
        const = find_constant_sites(nexus)
        print("Constant Sites: %s" % ",".join([str(i) for i in const]))
    if options.unique:
        unique = find_unique_sites(nexus)
        print("Unique Sites: %s" % ",".join([str(i) for i in unique]))
    if options.zeros:
        zeros = check_zeros(nexus)
        print("Zero Sites: %s" % ",".join([str(i) for i in zeros]))
    if options.remove:
        remove = [int(i) for i in parse_deltree(options.remove)]
        print("Remove: %s" % ",".join([str(i) for i in zeros]))
        
    newnexus = new_nexus_without_sites(nexus, set(const + unique + zeros + remove))
    
    # check for saving
    if newnexus is not None and newnexusname is not None:
        newnexus.write_to_file(newnexusname)
        print("New nexus written to %s" % newnexusname)
