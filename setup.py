#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

VERSION = __import__('manpkicli').VERSION

setup(

    name='manpkicli',

    version=VERSION,

    packages=find_packages(),

    author="Gaetan FEREZ",

    author_email="manpki@ferez.fr",

    description="ManPKI Client",
    long_description=open('README.md').read(),

    # Dependency Manager
    #
    # Ex: ["gunicorn", "docutils >= 0.3", "lxml==0.5a7"]
    install_requires=[
        "requests",
        "colorlog",
        "python-jose",
        "setuptools",
        "paramiko",
        "requests-unixsocket",
        "scp",
        "urllib3",
    ],

    # Manifest.IN
    #include_package_data=True,

    # Default Web Page
    url='http://github.com/GaetanF/manpki-cli',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
    ],

    scripts=['bin/manpki'],

    # Ex "cmd-name = package.module:function".
    # entry_points={
    #     'console_scripts': [
    #         'manpkid = manpki:main',
    #     ],
    # },
)
