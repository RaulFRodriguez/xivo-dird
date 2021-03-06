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

import unittest

from hamcrest import assert_that, equal_to, is_, contains
from mock import ANY, patch, Mock, sentinel as s

from xivo_dird.core.source_manager import SourceManager


class TestSourceManager(unittest.TestCase):

    @patch('xivo_dird.core.source_manager.parse_config_dir')
    @patch('stevedore.enabled.EnabledExtensionManager')
    def test_load_sources(self, extension_manager_init, mock_parse_config_dir):
        mock_parse_config_dir.return_value = []
        extension_manager = extension_manager_init.return_value
        enabled_backends = [
            'ldap',
            'xivo_phonebook',
        ]

        manager = SourceManager(enabled_backends, 'somedir')

        manager.load_sources()

        extension_manager_init.assert_called_once_with(
            namespace='xivo_dird.backends',
            check_func=manager.should_load_backend,
            invoke_on_load=False)
        extension_manager.map.assert_called_once_with(ANY, ANY)

    @patch('xivo_dird.core.source_manager.parse_config_dir')
    @patch('stevedore.enabled.EnabledExtensionManager')
    def test_load_sources_returns_dict_of_sources(self, extension_manager_init, mock_parse_config_dir):
        mock_parse_config_dir.return_value = []
        enabled_backends = [
            'ldap',
            'xivo_phonebook',
        ]

        manager = SourceManager(enabled_backends, 'somedir')
        manager._sources = s.sources

        result = manager.load_sources()

        assert_that(result, equal_to(s.sources))

    def test_should_load_backend(self):
        enabled_backends = [
            'ldap',
        ]
        backend_1 = Mock()
        backend_1.name = 'ldap'
        backend_2 = Mock()
        backend_2.name = 'xivo_phonebook'

        manager = SourceManager(enabled_backends, 'somedir')

        assert_that(manager.should_load_backend(backend_1), is_(True))
        assert_that(manager.should_load_backend(backend_2), is_(False))

    @patch('xivo_dird.core.source_manager.parse_config_dir')
    def test_load_all_configs(self, mock_parse_config_dir):
        manager = SourceManager([], 'foo')

        manager._load_all_configs()

        mock_parse_config_dir.assert_called_once_with('foo')

    def test_load_sources_using_backend_calls_load_on_all_sources_using_this_backend(self):
        configs = config1, config2 = [
            {
                'type': 'backend',
                'name': 'source1'
            },
            {
                'type': 'backend',
                'name': 'source2'
            }
        ]
        configs_by_backend = {
            'backend': configs
        }
        extension = Mock()
        extension.name = 'backend'
        source1, source2 = extension.plugin.side_effect = Mock(), Mock()
        manager = SourceManager([], 'somedir')

        manager._load_sources_using_backend(extension, configs_by_backend)

        assert_that(source1.name, equal_to('source1'))
        source1.load.assert_called_once_with({'config': config1})
        assert_that(source2.name, equal_to('source2'))
        source2.load.assert_called_once_with({'config': config2})

    def test_load_sources_using_backend_calls_load_on_all_sources_with_exceptions(self):
        configs = config1, config2 = [
            {
                'type': 'backend',
                'name': 'source1'
            },
            {
                'type': 'backend',
                'name': 'source2'
            }
        ]
        configs_by_backend = {
            'backend': configs
        }
        extension = Mock()
        extension.name = 'backend'
        source1, source2 = extension.plugin.side_effect = Mock(), Mock()
        source1.load.side_effect = RuntimeError
        manager = SourceManager([], 'somedir')

        manager._load_sources_using_backend(extension, configs_by_backend)

        assert_that(manager._sources.keys(), contains('source2'))
        assert_that(source2.name, equal_to('source2'))
        source2.load.assert_called_once_with({'config': config2})
