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

import abc


class DirectorySourcePlugin(object):
    '''
    This is the base class of a backend plugin. Each instance of these plugins
    is references to as a source.

    A variable named "Klass" should be defined in the module's global scope
    and the plugin class should be assigned to it.
    '''
    __metaclass__ = abc.ABCMeta

    def load(self, args=None):
        '''
        Bootstrap the plugin instance and acquire ressources that are required
        by the plugin instance to work properly
        '''

    def unload(self, args=None):
        '''
        Cleanup function that is called before the plugin instance is deleted
        '''

    def name(self):
        '''
        Returns the name of this plugin instance
        '''
        if hasattr(self, '_config'):
            return self._config.name

    @abc.abstractmethod
    def lookup(self, term, args):
        '''
        Returns a list of lookup result
        '''

    @abc.abstractmethod
    def reverse_lookup(self, term):
        '''
        Finds a name based on a number
        '''
