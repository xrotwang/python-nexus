from setuptools import setup, find_packages
from nexus import __version__ as version
from nexus import __doc__ as long_desc

setup(
    name="python-nexus", 
    version=version,
    description="A generic nexus (phylogenetics) file format (.nex, .trees) reader for python",
    long_description=long_desc,
    classifiers=[
        "Programming Language :: Python", 
        "Intended Audience :: Science/Research", 
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="phylogenetics nexus newick paup splitstree",
    author="Simon Greenhill",
    author_email="simon@simon.net.nz",
    url="http://simon.net.nz/articles/python-nexus",
    license="BSD",
    packages=['nexus'],
    package_dir={'nexus': 'nexus'},
    package_data={'nexus/examples': ['*.nex', '*.trees']},
    scripts=[
        'nexus/bin/nexus_combine_nexus.py',
        'nexus/bin/nexus_deinterleave.py',
        'nexus/bin/nexus_describecharacter.py',
        'nexus/bin/nexus_describetaxa.py',
        'nexus/bin/nexus_nexusmanip.py',
        'nexus/bin/nexus_randomise.py',
        'nexus/bin/nexus_tally.py',
        'nexus/bin/nexus_treemanip.py',
        'nexus/bin/nexus_anonymise.py',
    ],
)

