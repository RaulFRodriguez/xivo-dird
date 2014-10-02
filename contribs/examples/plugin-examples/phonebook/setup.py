#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='xivo-dird_phonebook_plugin',
    version='0.0.1',

    description='phonebook for XiVO dird',

    author='Avencall',
    author_email='dev@avencall.com',

    url='https://github.com/xivo-pbx/xivo-dird',

    packages=find_packages(),

    entry_points={
        'dird.sources': [
            'phonebook = src.phonebook:PhonebookPlugin',
        ],
        'dird.services': [
            'phonebook = src.phonebook:load',
        ],
    },
)
