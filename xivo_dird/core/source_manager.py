# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from collections import defaultdict
from stevedore import enabled
from xivo.config_helper import parse_config_dir


logger = logging.getLogger(__name__)


class SourceManager(object):

    _namespace = 'xivo_dird.backends'

    def __init__(self, enabled_backends, source_config_dir):
        self._enabled_backends = enabled_backends
        self._source_config_dir = source_config_dir
        self._configs_by_backend = defaultdict(list)
        self._sources = {}

    def should_load_backend(self, extension):
        return extension.name in self._enabled_backends

    def load_sources(self):
        manager = enabled.EnabledExtensionManager(
            namespace=self._namespace,
            check_func=self.should_load_backend,
            invoke_on_load=False,
        )
        self._load_all_configs()
        manager.map(self._load_sources_using_backend, self._configs_by_backend)
        return self._sources

    def _load_all_configs(self):
        source_configs = parse_config_dir(self._source_config_dir)

        for source_config in source_configs:
            if 'type' not in source_config:
                continue

            self._configs_by_backend[source_config['type']].append(source_config)

    def _load_sources_using_backend(self, extension, configs_by_backend):
        backend = extension.name
        for config in configs_by_backend[backend]:
            source = extension.plugin()
            source.name = config.get('name')
            try:
                source.load({'config': config})
                self._sources[source.name] = source
            except Exception:
                logger.exception('Failed to load %s', source.name)
