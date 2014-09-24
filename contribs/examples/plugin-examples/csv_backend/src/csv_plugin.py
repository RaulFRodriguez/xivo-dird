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

import csv
import logging

logger = logging.getLogger(__name__)

from xivo_dird.backends.directory_source_plugin import DirectorySourcePlugin


class CSVPlugin(DirectorySourcePlugin):

    def load(self, args=None):
        logger.debug('Loading with %s...', args)
        self._config = args
        self._read_directory_content(self._config['file'])
        logger.debug('Entries: %s', self._entries)

    def _read_directory_content(self, filename):
        self._entries = []
        with open(filename) as f:
            csv_reader = csv.reader(f)
            headers = next(csv_reader)
            for row in csv_reader:
                entry = {}
                for i, header in enumerate(headers):
                    entry[header] = row[i]
                self._entries.append(entry)

    def unload(self):
        logger.debug('Unloading.')

    def lookup(self, term, args):
        logger.debug('Looking up for %s', term)
        lower_term = term.lower()
        for entry in self._entries:
            if lower_term in entry['name'].lower():
                yield entry

    def reverse_lookup(self, term):
        logger.debug('Looking up for %s', term)
        for entry in self._entries:
            if entry['number'] == term:
                return entry['name']
