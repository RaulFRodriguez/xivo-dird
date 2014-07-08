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

from importlib import import_module

logger = logging.getLogger(__name__)


class PluginManager(object):

    def __init__(self, config):
        logger.debug('PluginManager')
        self._config = config
        self.load_all_backends()
        self._modules = {}

    def __del__(self):
        logger.debug('Bye')

    def load_all_backends(self):
        for plugin in self._get_plugins():
            module_name = 'xivo_dird.backends.%s' % plugin
            try:
                module = import_module(module_name)
                module.load()
            except ImportError:
                logger.warning('Could not find plugin %s' % module_name)

    def _load(self, plugin):
        module_name = 'xivo_dird.backends.%s' % plugin
        try:
            self._modules[plugin] = import_module(module_name)
            self._modules[plugin].load()
        except ImportError:
            logger.warning('Could not find plugin %s' % module_name)

    def _unload(self, plugin):
        if plugin not in self._modules:
            return
        self._modules[plugin].unload()

    def reload(self):
        plugins = self._get_plugins()
        for plugin in plugins:
            plugin.reload()

    def _get_plugins(self):
        if not self._config.has_section('plugins'):
            logger.debug('No plugin configured')
            return

        for plugin in self._config.options('plugins'):
            yield plugin
