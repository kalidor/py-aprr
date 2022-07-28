#! /usr/bin/env python

from setuptools import setup, find_packages
import sys

setup(
    name = 'pyaprr',
    version = '0.1',
    packages=find_packages(),
    scripts=['bin/aprr'],
    package_data={"pyaprr": ["data/peages-2017.csv"]},
    # Metadata
    author = 'Gregory Charbonneau',
    author_email = 'kalidor@unixed.fr', 
    description = 'Retrieve notes (Factures) from APRR',
    classifiers = [
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    license = 'WTFPLv2',
    install_requires = ['requests', 'rich']
)
