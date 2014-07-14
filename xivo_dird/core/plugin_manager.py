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

import os
import logging
import json

from importlib import import_module
from collections import namedtuple, defaultdict

logger = logging.getLogger(__name__)


ReverseLookupResult = namedtuple('ReverseLookupResult', ['result', 'query', 'source'])


class PluginManager(object):
    '''
    Some asumptions about the PluginManager
    Plugins are used to query different directory sources
    Header configuration is a configuration of the PluginManager
    '''

    def __init__(self, config):
        logger.debug('PluginManager')
        self._config = config
        self._plugins = {}
        plugin_configurations = self.load_plugin_configurations()
        self.load_all_backends(plugin_configurations)

    def load_plugin_configurations(self):
        paths = []

        for dir_path, _, file_names in os.walk(self._config.get('plugin_config_dir')):
            for file_name in file_names:
                paths.append(os.path.join(dir_path, file_name))

        result = defaultdict(list)

        for path in paths:
            with open(path) as f:
                raw_content = f.read()
                content = json.loads(raw_content)
                result[content['type']].append(content)

        return result

    def load_all_backends(self, plugin_configurations):
        for plugin_name in self._get_plugin_names():
            module_name = 'xivo_dird.backends.%s' % plugin_name
            try:
                logger.debug('Loading module %s', module_name)
                module = import_module(module_name)
                for plugin_configuration in plugin_configurations[plugin_name]:
                    instance = module.Klass(plugin_configuration)
                    instance.load()
                self._plugins[instance.name()] = instance
            except ImportError:
                logger.exception('Could not find plugin %s' % module_name)

    def _load(self, plugin):
        module_name = 'xivo_dird.backends.%s' % plugin
        try:
            self._plugins[plugin] = import_module(module_name)
            self._plugins[plugin].load()
        except ImportError:
            logger.warning('Could not find plugin %s' % module_name)

    def _unload(self, plugin):
        if plugin not in self._plugins:
            return
        self._plugins[plugin].unload()

    def reload(self):
        plugins = self._get_plugin_names()
        for plugin in plugins:
            plugin.reload()

    def reverse_lookup(self, term):
        for plugin in self._get_plugins():
            return ReverseLookupResult(plugin.reverse_lookup(term), term, plugin.name())

    def _get_plugins(self):
        for plugin in self._plugins.itervalues():
            yield plugin

    def _get_plugin_names(self):
        if 'plugins' not in self._config:
            logger.debug('No plugin configured')
            return

        for plugin in self._config.get('plugins'):
            yield plugin
