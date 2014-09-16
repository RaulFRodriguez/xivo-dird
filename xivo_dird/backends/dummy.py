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

import logging
import random
import time

from xivo_dird.backends.directory_source_plugin import DirectorySourcePlugin
from xivo_dird.backends.directory_source_plugin import SourceReverseLookupResult

logger = logging.getLogger(__name__)


class DummyPlugin(DirectorySourcePlugin):

    def __init__(self, config):
        self._config = config

    def load(self, args=None):
        logger.debug('Loading with %s', args)

    def unload(self, args=None):
        logger.debug('Unloading...')

    def lookup(self, term, args):
        logger.debug('Looking up for %s', term)
        for i in xrange(100):
            yield '%s %s' % (args.get('name', ['User'])[0], str(i))

    def reverse_lookup(self, term):
        logger.debug('Looking up for %s', term)
        time.sleep(random.random())
        name = self._config.reverse_result[ord(term[-1]) % len(self._config.reverse_result)]
        return SourceReverseLookupResult(name=name, number=term)


Klass = DummyPlugin
