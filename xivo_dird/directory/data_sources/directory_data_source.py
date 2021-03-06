# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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


class DirectoryDataSource(object):

    @staticmethod
    def _get_key_mapping(contents):
        # Return a dictionary mapping std key to src key
        key_mapping = {}
        for k, v in contents.iteritems():
            if k.startswith('field_'):
                # strip the leading 'field_' and add a leading 'db-'
                std_key = 'db-' + k[6:]
                # XXX right now we only handle 1 src key per std key
                key_mapping[std_key] = v[0]
        return key_mapping
