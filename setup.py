#!/usr/bin/env python3.4
# coding: utf-8

import modulable

from setuptools import setup


with open('README.rst') as description:
    setup(
        name='modulable',
        version=modulable.__version__,
        description='A lightweight library for writing modular code',
        long_description = description.read(),
        author='baxbaxwalanuksiwe',
        author_email='baxbaxwalanuksiwe@gmail.com',
        license='MIT',
        platforms='any',
        url='https://github.com/felko/modulable',
        download_url='https://github.com/felko/modulable',
        keywords = [],
        classifiers = [
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Utilities'
        ]
    )
