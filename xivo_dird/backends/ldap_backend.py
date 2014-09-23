# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import ldap
import logging
import random
import time

from xivo_dird.backends.directory_source_plugin import DirectorySourcePlugin
from xivo_dird.backends.directory_source_plugin import SourceReverseLookupResult

logger = logging.getLogger(__name__)


class LDAPPlugin(DirectorySourcePlugin):

    def load(self, args=None):
        logger.debug('Loading with %s', args)
        self._config = args
        self._ldap = ldap.initialize(args['uri'])
        self._ldap.simple_bind(args['login'], args['password'])

    def unload(self, args=None):
        logger.debug('Unloading...')

    def lookup(self, term, args):
        logger.debug('Looking up for %s', term)
        logger.debug('config: %s', self._config)
        results = self._ldap.search_s(self._config['search_base'],
                                      ldap.SCOPE_SUBTREE,
                                      filterstr='(|(sn=*{term}*)(givenName=*{term}*))'.format(term=term))
        return results

    def reverse_lookup(self, term):
        logger.debug('Looking up for %s', term)
        time.sleep(random.random())
        name = self._config['reverse_result'][ord(term[-1]) % len(self._config['reverse_result'])]
        return SourceReverseLookupResult(name=name, number=term)
