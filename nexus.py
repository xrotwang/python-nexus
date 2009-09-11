#!/usr/bin/env python
"""
Generic nexus (.nex) reader for python

>>> nex = Nexus('examples/example.nex')
>>> nex.blocks
{'data': <NexusDataBlock: 2 characters from 4 taxa>}

>>> nex.blocks['data'].nchar
2

>>> nex.blocks['data'].ntaxa
4

>>> nex.blocks['data'].matrix
{'Simon': ['01'], 'Louise': ['11'], 'Betty': ['10'], 'Harry': ['00']}

>>> nex.blocks['data'].matrix['Simon']
['01']

>>> sorted(nex.blocks['data'].taxa)
['Betty', 'Harry', 'Louise', 'Simon']

>>> sorted(nex.blocks['data'].matrix.keys())
['Betty', 'Harry', 'Louise', 'Simon']


Class Nexus is a generic object for loading nexus information.

The Handlers are objects to store specialised blocks found in nexus files, and 
are initialised in Nexus.known_blocks: 

    Nexus.known_blocks = {
        'trees': TreeHandler,
        'data': DataHandler,
    }
    
    ...adding a specialised handler for a certain block type is as easy as subclassing GenericHandler,
    and attaching it into the Nexus known_blocks dictionary under the block label, e.g.
    
    n = Nexus()
    n.known_blocks['r8s'] = R8sBlockHandler
    n.read_file('myfile.nex')
    print n.blocks['r8s']
"""
__author__ = 'Simon Greenhill <simon@simon.net.nz>'

import re

DEBUG = False

BEGIN_PATTERN = re.compile(r"""begin (\w+);""", re.IGNORECASE)
END_PATTERN1 = re.compile(r"""end;""", re.IGNORECASE)
END_PATTERN2 = re.compile(r"""^;$""")
NTAX_PATTERN = re.compile(r"""NTAX=(\d+)""", re.IGNORECASE)
NCHAR_PATTERN = re.compile(r"""NCHAR=(\d+)""", re.IGNORECASE)
COMMENT_PATTERN = re.compile(r"""(\[.*?\])""")

class GenericHandler(object):
    def __init__(self):
        """Initialise datastore in <storage> under <keyname>"""
        self.storage = []
        
    def parse(self, data):
        for line in data:
            self.storage.append(line)
            
    def remove_comments(self, line):
        """
        Removes comments from lines
        
        >>> g = GenericHandler()
        >>> g.remove_comments("Hello [world]")
        'Hello '
        >>> g.remove_comments("He[bite]ll[me]o")
        'Hello'
        """
        return COMMENT_PATTERN.sub('', line)
    
    
class TreeHandler(GenericHandler):
    """Handler for `trees` blocks"""
    def parse(self, data):
        self.storage.append(data)
        
class DataHandler(GenericHandler):
    """Handler for data matrices"""
    def __init__(self):
        self.taxa = []
        self.ntaxa = 0
        self.nchar = 0
        self.format = {}
        self.gaps = None
        self.missing = None
        self.matrix = {}
    
    def _parse_format_line(self, line):
        """
        Parses a format line, and returns a dictionary of tokens
        
        >>> d = DataHandler()._parse_format_line('Format datatype=standard symbols="01" gap=-;')
        >>> assert d['datatype'] == 'standard', "Expected 'standard', but got '%s'" % d['datatype']
        >>> assert d['symbols'] == '01', "Expected '01', but got '%s'" % d['symbols']
        >>> assert d['gap'] == '-', "Expected 'gap', but got '%s'" % d['gap']
        
        >>> d = DataHandler()._parse_format_line('FORMAT datatype=RNA missing=? gap=- symbols="ACGU" labels interleave;')
        >>> assert d['datatype'] == 'rna', "Expected 'rna', but got '%s'" % d['datatype']
        >>> assert d['missing'] == '?', "Expected '?', but got '%s'" % d['missing']
        >>> assert d['gap'] == '-', "Expected '-', but got '%s'" % d['gap']
        >>> assert d['symbols'] == 'acgu', "Expected 'acgu', but got '%s'" % d['symbols']
        >>> assert d['labels'] == True, "Expected <True>, but got '%s'" % d['labels']
        >>> assert d['interleave'] == True, "Expected <True>, but got '%s'" % d['interleave']
        """
        out = {}
        line = line.lower()
        # cleanup
        line = line.lstrip('format').strip(';').strip().replace('"', '')
        for chunk in line.split():
            try:
                k, v = chunk.split("=")
            except ValueError:
                k, v = chunk, True
            out[k] = v
        return out
        
        
    def parse(self, data):
        for line in data:
            lline = line.lower()
            # Dimensions line
            if lline.startswith('dimensions '):
                # try for nchar/ntax
                self.ntaxa = int(NTAX_PATTERN.findall(line)[0])
                self.nchar = int(NCHAR_PATTERN.findall(line)[0])
            
            # handle format line
            elif lline.startswith('format '):
                self.format = self._parse_format_line(line)
            elif lline.startswith('matrix'):
                seen_matrix = True
                continue
            # ignore a few things..
            elif BEGIN_PATTERN.match(line):
                continue
            elif 'charstatelabels' in lline:
                raise NotImplementedError, 'Character block parsing is not implemented yet'
            elif seen_matrix == True:
                try:
                    taxon, sites = line.split(' ', 1)
                except ValueError:
                    continue
                
                taxon = taxon.strip()
                sites = sites.strip()
                
                if taxon not in self.taxa:
                    self.taxa.append(taxon)
                
                self.matrix[taxon] = self.matrix.get(taxon, [])
                self.matrix[taxon].append(sites)
        
    def __repr__(self):
        return "<NexusDataBlock: %d characters from %d taxa>" % (self.nchar, self.ntaxa)
        

class Nexus(object):
    blocks = {}
    rawblocks = {}
    log = []
    known_blocks = {
        'trees': TreeHandler,
        'data': DataHandler,
    }
    
    def __init__(self, filename):
        if filename:
            return self.read_file(filename)
        
    def _do_blocks(self):
        for block, data in self.raw_blocks.iteritems():
            self.blocks[block] = self.known_blocks.get(block, GenericHandler)()
            self.log.append('Read block: %s with %d lines, parsing with %s' % (block, len(data), self.blocks[block])) 
            self.blocks[block].parse(data)
    
    def read_file(self, filename):
        """
        Loads and Parses a Nexus File
        """
        self.filename = filename
        try:
            handle = open(filename, 'rU')
        except IOError:
            raise IOError, "Unable To Read File %s" % input
        
        store = {}
        block = None
        for line in handle.xreadlines():
            line = line.strip()
            if len(line) == 0:
                continue
            elif line.startswith('[') and line.endswith(']'):
                continue
            
            # check if we're in a block and initialise
            found = BEGIN_PATTERN.findall(line)
            if found:
                block = found[0].lower()
                if store.has_key(block):
                    raise Exception, "Duplicate Block %s" % block
                store[block] = []
                
            # check if we're ending a block
            if END_PATTERN1.search(line) or END_PATTERN2.search(line):
                block = None
                
            if block is not None:
                store[block].append(line)
        handle.close()
        
        self.raw_blocks = store
        self._do_blocks()
        return


if __name__ == '__main__':
    n = Nexus('examples/example.nex')
    for k, v in n.nexus.iteritems():
        print k
        print v
        print
    
    # n = Nexus('examples/example.nex.trees')
    # for k, v in n.nexus.iteritems():
    #     print k
    #     print v
    #     print
    
    