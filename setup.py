# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages

version = '0.0.1'


try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])

if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

SETUP_DIR = os.path.abspath(SETUP_DIRNAME)
REQUIREMENTS_DIR = os.path.join('requirements')
INSTALL_REQS = os.path.join(REQUIREMENTS_DIR, 'install.txt')
# TEST_REQS = os.path.join(REQUIREMENTS_DIR, 'test.txt')
# DEVELOPMENT_REQS = os.path.join(REQUIREMENTS_DIR, 'development.txt')


def read(fname):
    return open(fname).read()


def get_reqs(filename):
    reqs = []
    with open(filename) as handle:
        for line in handle.readlines():
            if not line or line.startswith('#'):
                continue
            reqs.append(line.strip())
    return reqs


# Build a list of req
install_requires = get_reqs(INSTALL_REQS)
# test_requires = install_requires + get_reqs(TEST_REQS)
# dev_requires = test_requires + get_reqs(DEVELOPMENT_REQS)


setup(
    name='flask-concierge',
    version=version,
    author='',
    author_email='',
    url='',
    description='',
    long_description=read('README.mdown'),
    packages=find_packages(
        exclude=["fabfile", "tests"]),
    include_package_data=True,
    zip_safe=False,
    # Dependencies
    install_requires=install_requires,
    # extras_require={
    #     'test': test_requires,
    #     'develop': dev_requires},
    # Classifiers for Package Indexing
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'])
