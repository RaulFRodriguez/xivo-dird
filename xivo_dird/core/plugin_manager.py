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
import os
import yaml

from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED
from collections import namedtuple
from collections import defaultdict
from stevedore import enabled

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
        self._mgr = enabled.EnabledExtensionManager(
            namespace='dird.sources',
            check_func=self._plugin_filter,
            invoke_on_load=False,
        )
        self._plugin_config = self._build_plugin_config()
        self._sources = []
        self._profile_sources = defaultdict(list)

    def _plugin_filter(self, extension):
        return extension.name in self._config.plugins

    def _build_plugin_config(self):
        '''
        Fetch all plugin configurations

        Returns a dictionnary of list of configurations. The dictionnary keys are
        plugin types and the values are list of configurations for each instances.
        '''
        configs = defaultdict(list)
        paths = []
        for dir_path, _, file_names in os.walk(self._config.plugin_config_dir):
            for file_name in file_names:
                paths.append(os.path.join(dir_path, file_name))

        for path in paths:
            with open(path) as f:
                config = yaml.load(f)
                configs[config['type']].append(config)

        return configs

    def _load(self, extension):
        '''
        This function is responsible on the instanciation and setup
        of each plugin instances.
        '''
        plugin_type = extension.name
        for plugin_config in self._plugin_config[plugin_type]:
            source = extension.plugin()
            source.load(plugin_config)
            self._sources.append(source)

    def _init_profile_map(self):
        logger.debug('Initializing profile sources')
        for profile in self._config.lookup_directories.__dict__:
            source_names = self._get_profile_lookup_sources(profile)
            logger.debug('%s should contain %s', profile, source_names)
            for source in self._sources:
                logger.debug('Checking %s in %s', source.name(), source_names)
                if source.name() in source_names:
                    self._profile_sources[profile].append(source)

    def _get_profile_lookup_sources(self, profile):
        return getattr(self._config.lookup_directories, profile, [])

    def start(self):
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._mgr.map(self._load)
        self._init_profile_map()

    def stop(self):
        self._executor.shutdown()

    def _async_lookup(self, source, term, args):
        logger.debug('Launching an async search in %s', source)
        future = self._executor.submit(source.lookup, term, args)
        future.name = source.name()
        return future

    def lookup(self, profile, term, args):
        pending_futures = [self._async_lookup(s, term, args)
                           for s in self._profile_sources[profile]]
        presents, _ = wait(pending_futures, return_when=ALL_COMPLETED)
        return [LookupResult(p.result(), term, args, p.name) for p in presents]

    def _async_reverse_lookup(self, plugin, term):
        future = self._executor.submit(plugin.reverse_lookup, term)
        future.name = plugin.name()
        return future

    def reverse_lookup(self, term):
        pending_futures = [self._async_reverse_lookup(s, term)
                           for s in self._sources
                           if s.name() in self._config.reverse_directories]

        # Return when the first not None result is found
        presents, _ = wait(pending_futures, return_when=FIRST_COMPLETED)
        p = presents.pop()
        try:
            return ReverseLookupResult(p.result(), term, p.name)
        except IndexError:
            return None
