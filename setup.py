#!/usr/bin/env python3.4
# coding: utf-8

import modulable

from setuptools import setup


with open('README.md') as description:
    setup(
        name='modulable',
        version=modulable.__version__,
        description='A lightweight library for writing modular code',
        author='baxbaxwalanuksiwe',
        author_email='baxbaxwalanuksiwe@gmail.com',
        url='https://github.com/felko/modulable',
        long_description = description.read(),
        download_url='https://github.com/felko/modulable',
        keywords = [],
        classifiers = [
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3 :: Only',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Utilities'
        ]
    )
