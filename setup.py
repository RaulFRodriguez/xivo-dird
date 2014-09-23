#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='xivo-dird',
    version='0.0.1',

    description='XiVO Directory Daemon',

    author='Avencall',
    author_email='dev@avencall.com',

    url='https://github.com/xivo-pbx/xivo-dird',

    packages=find_packages(),

    scripts=['bin/xivo-dird'],

    entry_points={
        'dird.sources': [
            'ldap = xivo_dird.backends.ldap_backend:LDAPPlugin',
            'dummy = xivo_dird.backends.dummy:DummyPlugin',
        ],
    },
)
