#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='xivo-dird_csv_backend',
    version='0.0.1',

    description='a CSV file directory backend for XiVO dird',

    author='Avencall',
    author_email='dev@avencall.com',

    url='https://github.com/xivo-pbx/xivo-dird',

    packages=find_packages(),

    entry_points={
        'dird.sources': [
            'csv = src.csv_plugin:CSVPlugin',
        ],
    },
)
