"""Regression Tests"""
import os
import re
import unittest
from nexus import NexusReader

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), '../examples')
REGRESSION_DIR = os.path.join(os.path.dirname(__file__), 'regression')


class Test_DataHandler_Regression_WhitespaceInMatrix(unittest.TestCase):
    """
    Regression: Test that leading whitespace in a data matrix is parsed ok
    """
    def test_regression(self):
        nex = NexusReader(
            os.path.join(REGRESSION_DIR, 'white_space_in_matrix.nex')
        )
        assert nex.blocks['data'].nchar == 2
        assert nex.blocks['data'].matrix['Harry'] == ['0', '0']
        assert nex.blocks['data'].matrix['Simon'] == ['0', '1']
        assert nex.blocks['data'].matrix['Betty'] == ['1', '0']
        assert nex.blocks['data'].matrix['Louise'] == ['1', '1']



class Test_TreeHandler_Regression_RandomAPETrees(unittest.TestCase):
    """Regression: Test that we can parse randomly generated APE/R trees"""
    def test_regression(self):
        nex = NexusReader(os.path.join(REGRESSION_DIR, 'ape_random.trees'))
        assert nex.trees.ntrees == 2


class Test_TreeHandler_Regression_BadCharsInTaxaName(unittest.TestCase):
    def setUp(self):
        self.nex = NexusReader(
            os.path.join(REGRESSION_DIR, 'bad_chars_in_taxaname.trees')
        )
    
    def test_trees(self):
        # did we get a tree block?
        assert 'trees' in self.nex.blocks
        # did we find 3 trees?
        assert len(self.nex.blocks['trees'].trees) == 1
        assert self.nex.blocks['trees'].ntrees == 1
    
    def test_translation(self):
        # did we get the translation parsed properly.
        assert self.nex.trees.was_translated
        assert len(self.nex.trees.translators) == 5
        # check last entry
        assert self.nex.trees.translators['5'] == 'PALAUNGWA_De.Ang'
    
    def test_detranslate(self):
        # check detranslate
        self.nex.trees.detranslate()
        expected = '(MANGIC_Bugan,MANGIC_Paliu,MANGIC_Mang,PALAUNGWA_Danaw,PAL'
        assert expected in self.nex.trees[0]


class Test_TreeHandler_Regression_DetranslateWithDash(unittest.TestCase):
    def setUp(self):
        self.nex = NexusReader(
            os.path.join(REGRESSION_DIR, 'detranslate-with-dash.trees')
        )

    def test_trees(self):
        # did we get a tree block?
        assert 'trees' in self.nex.blocks
        # did we find 3 trees?
        assert len(self.nex.blocks['trees'].trees) == 1
        assert self.nex.blocks['trees'].ntrees == 1
    
    def test_translate(self):
        # did we get the translation parsed properly.
        assert self.nex.trees.was_translated
        assert len(self.nex.trees.translators) == 5
    
    def test_regression(self):
        # check last entry
        assert self.nex.trees.translators['4'] == 'four-1'
        assert self.nex.trees.translators['5'] == 'four_2'
    
    def test_detranslate(self):
        # check detranslate
        self.nex.trees.detranslate()
        assert '(one,two,three,four-1,four_2)' in self.nex.trees[0]


class Test_TreeHandler_Regression_BranchLengthsInIntegers(unittest.TestCase):
    def setUp(self):
        self.nex = NexusReader(
            os.path.join(REGRESSION_DIR, 'branchlengths-in-integers.trees')
        )

    def test_trees(self):
        # did we get a tree block?
        assert 'trees' in self.nex.blocks
        # did we find 3 trees?
        assert len(self.nex.blocks['trees'].trees) == 1
        assert self.nex.blocks['trees'].ntrees == 1
    
    def test_translation(self):
        # did we get the translation parsed properly.
        assert self.nex.trees.was_translated
        assert len(self.nex.trees.translators) == 5
    
    def test_detranslate(self):
        # check detranslate
        self.nex.trees.detranslate()
        assert '(one:0.1,two:0.2,three:1,four:3,five:0.3)' in self.nex.trees[0]


class Test_TaxaHandler_Regression_Mesquite(unittest.TestCase):
    """Regression: Test that we can parse MESQUITE taxa blocks"""
    def setUp(self):
        self.nex = NexusReader(
            os.path.join(REGRESSION_DIR, 'mesquite_taxa_block.nex')
        )

    def test_taxa_block(self):
        for taxon in ['A', 'B', 'C']:
            assert taxon in self.nex.taxa
        # did we get the right number of taxa in the matrix?
        assert self.nex.taxa.ntaxa == len(self.nex.taxa.taxa) == 3

    def test_taxa_block_attributes(self):
        assert 'taxa' in self.nex.blocks
        assert len(self.nex.taxa.attributes) == 2
        assert 'TITLE Untitled_Block_of_Taxa;' in self.nex.taxa.attributes
        assert 'LINK Taxa = Untitled_Block_of_Taxa;' in self.nex.taxa.attributes
    
    def test_write(self):
        expected_patterns = [
            '^begin taxa;$',
            '^\s+TITLE Untitled_Block_of_Taxa;$',
            '^\s+dimensions ntax=3;$',
            '^\s+taxlabels$',
            "^\s+\[1\] 'A'$",
            "^\s+\[2\] 'B'$",
            "^\s+\[3\] 'C'$",
            '^;$',
            '^end;$',
        ]
        written = self.nex.write()
        for expected in expected_patterns:
            assert re.search(expected, written, re.MULTILINE), \
                'Expected "%s"' % expected


class Test_DataHandler_Regression_Mesquite(unittest.TestCase):
    """Regression: Test that we can parse MESQUITE data blocks"""

    def setUp(self):
        self.nex = NexusReader()
        self.nex.read_string("""
        #NEXUS

        Begin data;
        TITLE Untitled_Block_of_Taxa;
        LINK Taxa = Untitled_Block_of_Taxa;
        Dimensions ntax=2 nchar=2;
        Format datatype=standard gap=- symbols="01";
        Matrix
        Harry              00
        Simon              01
            ;
        End;
        """)
    
    def test_attributes(self):
        assert len(self.nex.data.attributes) == 2
        assert self.nex.data.attributes[0] == \
            """TITLE Untitled_Block_of_Taxa;"""
        assert self.nex.data.attributes[1] == \
            """LINK Taxa = Untitled_Block_of_Taxa;"""

    def test_write(self):
        expected_patterns = [
            '^begin data;$',
            '^\s+TITLE Untitled_Block_of_Taxa;$',
            '^\s+LINK Taxa = Untitled_Block_of_Taxa;$',
            '^\s+dimensions ntax=2 nchar=2;$',
            '^\s+format datatype=standard gap=- symbols="01";$',
            "^matrix$",
            "^Harry\s+00",
            "^Simon\s+01$",
            '^\s+;$',
            '^end;$',
        ]
        written = self.nex.write()
        for expected in expected_patterns:
            assert re.search(expected, written, re.MULTILINE), \
                'Expected "%s"' % expected


class Test_TreeHandler_Regression_Mesquite(unittest.TestCase):
    """Regression: Test that we can parse MESQUITE taxa blocks"""
    def setUp(self):
        self.nex = NexusReader(
            os.path.join(REGRESSION_DIR, 'mesquite_formatted_branches.trees')
        )

    def test_attributes(self):
        assert len(self.nex.trees.attributes) == 2
        assert self.nex.trees.attributes[0] == \
            """Title 'Trees from "temp.trees"';"""
        assert self.nex.trees.attributes[1] == \
            """LINK Taxa = Untitled_Block_of_Taxa;"""

    def test_found_trees(self):
        assert self.nex.trees.ntrees == 1

    def test_found_taxa(self):
        assert len(self.nex.trees.taxa) == 3
        assert 'A' in self.nex.trees.taxa
        assert 'B' in self.nex.trees.taxa
        assert 'C' in self.nex.trees.taxa

    def test_was_translated(self):
        assert self.nex.trees.was_translated

    def test_translation(self):
        assert self.nex.trees.translators['1'] == 'A'
        assert self.nex.trees.translators['2'] == 'B'
        assert self.nex.trees.translators['3'] == 'C'

    def test_write(self):
        written = self.nex.write()
        assert """Title 'Trees from "temp.trees"';""" in written
        assert """LINK Taxa = Untitled_Block_of_Taxa;""" in written



class Test_TaxaHandler_OneLine(unittest.TestCase):
    """
    Regression: 
    Test that we can read taxalabels delimited by spaces not new lines.
    """
    def setUp(self):
        self.nex = NexusReader(
            os.path.join(REGRESSION_DIR, 'taxlabels.nex')
        )
    
    def test_block_find(self):
        assert 'taxa' in self.nex.blocks
        
    def test_taxa(self):
        for taxon in ['A', 'B', 'C']:
            assert taxon in self.nex.data.matrix
            assert taxon in self.nex.blocks['taxa'].taxa
        assert self.nex.blocks['taxa'].ntaxa == 3
    
    def test_block_find(self):
        assert 'data' in self.nex.blocks

    def test_charblock_find(self):
        assert hasattr(self.nex.data, 'characters')

    def test_data_ntaxa(self):
        assert self.nex.data.ntaxa == 3

    def test_data_nchar(self):
        assert self.nex.data.nchar == 3

    def test_matrix(self):
        assert self.nex.data.matrix["A"] == ["1", "1", "1"]
        assert self.nex.data.matrix["B"] == ["0", "1", "1"]
        assert self.nex.data.matrix["C"] == ["0", "0", "1"]
        


if __name__ == '__main__':
    unittest.main()
