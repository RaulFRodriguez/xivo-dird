#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

setup(
    name='xivo-dird',
    version='1.2',

    description='XiVO Directory Daemon',

    author='Avencall',
    author_email='dev@avencall.com',

    url='https://github.com/xivo-pbx/xivo-dird',

    packages=find_packages(),

    scripts=['bin/xivo-dird'],

    entry_points={
        'xivo-dird.services': [
            'lookup = xivo_dird.plugins.lookup:LookupServicePlugin',
        ],
        'xivo-dird.backends': [
            'csv = xivo_dird.plugins.csv_plugin:CSVPlugin',
        ],
        'xivo-dird.views': [
            'default_json_view = xivo_dird.plugins.default_json_view:JSonViewPlugin',
        ],
    }
)
