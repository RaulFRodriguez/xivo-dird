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
from xivo_dird.core.directory_source_handle import DirectorySourceHandle

logger = logging.getLogger(__name__)


ReverseLookupResult = namedtuple('ReverseLookupResult', ['result', 'query', 'source'])
LookupResult = namedtuple('LookupResult', ['results', 'query', 'args', 'source'])


class PluginManager(object):
    '''
    Some asumptions about the PluginManager
    Plugins are used to query different directory sources
    Header configuration is a configuration of the PluginManager
    '''

    def __init__(self, config):
        logger.debug('PluginManager')
        self._config = config
        self._sources = {}
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
                for source_configuration in plugin_configurations[plugin_name]:
                    name, handle = self._setup_plugin_handle(module.Klass, source_configuration)
                    # instance = module.Klass(plugin_configuration)
                    # instance.load()
                    self._sources[name] = handle
            except ImportError:
                logger.exception('Could not find plugin %s' % module_name)

    def _setup_plugin_handle(self, plugin_class, source_configuration):
        handle = DirectorySourceHandle(plugin_class, source_configuration)
        return handle.name(), handle

    def lookup(self, profile, term, args):
        results = []
        for lookup_source in self._get_lookup_sources(profile):
            results.append(LookupResult(lookup_source.lookup(term, args),
                                        term,
                                        args,
                                        lookup_source.name()))

        return results

    def reverse_lookup(self, term):
        queues, name = [], None
        for reverse_source in self._get_reverse_sources():
            queues.append(reverse_source.reverse_lookup(term))

        # Return when the first not None result is found
        while True:
            to_remove = []
            for q in queues:
                if not q.empty():
                    result = q.get_nowait()
                    if result:
                        name = q.name
                        break
                    to_remove.append(q)

            for q in to_remove:
                queues.remove(q)

        return ReverseLookupResult(result, term, name)

    def _get_reverse_sources(self):
        for reverse_name in self._config.get('reverse_directories'):
            yield self._sources[reverse_name]

    def _get_lookup_sources(self, profile):
        for lookup_name in self._config.get('lookup_directories').get(profile):
            yield self._sources[lookup_name]

    def _get_plugins(self):
        for plugin in self._sources.itervalues():
            yield plugin

    def _get_plugin_names(self):
        if 'plugins' not in self._config:
            logger.debug('No plugin configured')
            return

        for plugin in self._config.get('plugins'):
            yield plugin
