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

logger = logging.getLogger(__name__)

PLUGIN_NAME = 'Dummy'


def load(args=None):
    logger.debug('Loading with %s', args)


def unload(args=None):
    logger.debug('Unloading...')


def reload(args=None):
    logger.debug('Reloading')


def lookup(term):
    for i in xrange(100):
        yield 'User %s' % i, str(i)


def reverse_lookup(term):
    logger.debug('Looking up for %s', term)
    return 'Lol'


def name():
    return PLUGIN_NAME