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
import yaml

from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED
from importlib import import_module
from collections import namedtuple, defaultdict
from xivo_dird.config import ConfigXivoDird

logger = logging.getLogger(__name__)


ReverseLookupResult = namedtuple('ReverseLookupResult', ['result', 'query', 'source'])
LookupResult = namedtuple('LookupResult', ['results', 'query', 'args', 'source'])


class PluginManager(object):
    '''
    Some assumptions about the PluginManager
    Plugins are used to query different directory sources
    Header configuration is a configuration of the PluginManager
    '''

    def __init__(self, config):
        logger.debug('PluginManager')
        self._config = config
        self._sources = {}
        plugin_configurations = self.load_plugin_configurations()
        self.load_all_backends(plugin_configurations)

    def start(self):
        self._executor = ThreadPoolExecutor(max_workers=10)

    def stop(self):
        self._executor.shutdown()

        for source in self._sources.itervalues():
            source.unload()

    def load_plugin_configurations(self):
        paths = []

        for dir_path, _, file_names in os.walk(self._config.plugin_config_dir):
            for file_name in file_names:
                paths.append(os.path.join(dir_path, file_name))

        result = defaultdict(list)

        for path in paths:
            with open(path) as f:
                try:
                    content = ConfigXivoDird(yaml.load(f))
                except ValueError:
                    logger.exception('Error while loading %s', path)
                result[content.type].append(content)

        return result

    def load_all_backends(self, plugin_configurations):
        for plugin_name in self._get_plugin_names():
            module_name = 'xivo_dird.backends.%s' % plugin_name
            try:
                logger.debug('Loading module %s', module_name)
                module = import_module(module_name)
                for source_configuration in plugin_configurations[plugin_name]:
                    source = module.Klass(source_configuration)
                    self._sources[source.name()] = source
            except ImportError:
                logger.exception('Could not find plugin %s' % module_name)

    def lookup(self, profile, term, args):
        pending_futures = set()
        for lookup_source in self._get_lookup_sources(profile):
            name = lookup_source.name()
            future = self._executor.submit(lookup_source.lookup, term, args)
            future.name = name
            pending_futures.add(future)

        presents, _ = wait(pending_futures, return_when=ALL_COMPLETED)
        results = []
        for present in presents:
            results.append(LookupResult(present.result(), term, args, present.name))

        return results

    def reverse_lookup(self, term):
        pending_futures = set()
        for reverse_source in self._get_reverse_sources():
            name = reverse_source.name()
            future = self._executor.submit(reverse_source.reverse_lookup, term)
            future.name = name
            pending_futures.add(future)

        # Return when the first not None result is found
        presents, _ = wait(pending_futures, return_when=FIRST_COMPLETED)
        p = presents.pop()
        try:
            return ReverseLookupResult(p.result(), term, p.name)
        except IndexError:
            return None

    def _get_reverse_sources(self):
        for reverse_name in self._config.reverse_directories:
            yield self._sources[reverse_name]

    def _get_lookup_sources(self, profile):
        for lookup_name in getattr(self._config.lookup_directories, profile):
            yield self._sources[lookup_name]

    def _get_plugins(self):
        for plugin in self._sources.itervalues():
            yield plugin

    def _get_plugin_names(self):
        if not self._config.plugins:
            logger.debug('No plugin configured')
            return

        for plugin in self._config.plugins:
            yield plugin
