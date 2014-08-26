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

import argparse
import json
import logging
import os
import signal

from flup.server.fcgi import WSGIServer

from xivo.daemonize import pidfile_context
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging
from xivo_dird import dird_server
from xivo_dird import core

logger = logging.getLogger(__name__)

_DAEMONNAME = 'xivo-dird'
_LOG_FILENAME = '/var/log/{}.log'.format(_DAEMONNAME)
_PID_FILENAME = '/var/run/{daemon}/{daemon}.pid'.format(daemon=_DAEMONNAME)
_SOCKET_FILENAME = '/tmp/{daemon}.sock'.format(daemon=_DAEMONNAME)
_DEFAULT_CONFIG_FILENAME = '/etc/xivo/xivo-dird/xivo-dird.conf'


class _ConfigReloadRequested(BaseException):
    pass


should_load_config = False


def main():
    global should_load_config
    should_load_config = True

    parsed_args = _parse_args()

    if parsed_args.user:
        change_user(parsed_args.user)

    setup_logging(_LOG_FILENAME, parsed_args.foreground, parsed_args.debug)

    signal.signal(signal.SIGUSR1, handler)

    while should_load_config:
        try:

            with open(parsed_args.config) as config_file:
                config = json.load(config_file)
            should_load_config = False

            with pidfile_context(_PID_FILENAME, parsed_args.foreground):
                _run(config, parsed_args.debug)

        except _ConfigReloadRequested:
            logger.debug('Config reload requested')
            should_load_config = True


def handler(signum, frame):
    logger.debug('Catched SIGUSR1')
    raise _ConfigReloadRequested()


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',
                        '--foreground',
                        action='store_true',
                        default=False,
                        help="Foreground, don't daemonize. Default: %(default)s")
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        default=False,
                        help="Enable debug messages. Default: %(default)s")
    parser.add_argument('-u',
                        '--user',
                        action='store',
                        help='The owner of the process.')
    parser.add_argument('-c',
                        '--config',
                        default=_DEFAULT_CONFIG_FILENAME,
                        action='store',
                        help='The path to the configuration file')
    return parser.parse_args()


def _run(config, debug=False):
    logger.debug('WSGIServer starting with uid %s', os.getuid())
    plugin_manager = dird_server.app.backend_plugin_manager = core.PluginManager(config)
    plugin_manager.start()
    WSGIServer(dird_server.app,
               bindAddress=_SOCKET_FILENAME,
               multithreaded=True,
               multiprocess=False,
               debug=debug).run()
    plugin_manager.stop()
