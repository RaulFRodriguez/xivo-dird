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
import signal
import thread

from flup.server.fcgi import WSGIServer

from xivo.daemonize import pidfile_context
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging
from xivo_dird import dird_server
from xivo_dird import core
from xivo_dird.bus.consumer import Consumer
from xivo_dird.config import config

logger = logging.getLogger(__name__)
wsgi_server = None
_reload = None


def main():
    setup_logging(config._LOG_FILENAME, config.foreground, config.debug)
    if config.user:
        change_user(config.user)

    bus_consumer = Consumer(config.bus_config_obj,
                            callback=ask_for_reload,
                            routing_key='config.directory.sources.*')
    thread.start_new_thread(bus_consumer.run, ())

    with pidfile_context(config._PID_FILENAME, config.foreground):
        _run()


def ask_for_reload(body):
    global _reload

    if body['name'] == 'directory_source_edited':
        logger.info('received')
        if wsgi_server:
            _reload = True
            # wsgi_server.shutdown() only available with flup 1.0.3
            os.kill(os.getpid(), signal.SIGHUP)


def _init_signal():
    signal.signal(signal.SIGTERM, _handle_sigterm)


def _handle_sigterm(signum, frame):
    raise SystemExit()


def _run():
    global wsgi_server
    global _reload

    _init_signal()

    while True:
        _reload = False
        plugin_manager = dird_server.app.backend_plugin_manager = core.PluginManager(config)
        plugin_manager.start()
        logger.info('WSGIServer starting with uid %s', os.getuid())
        wsgi_server = WSGIServer(dird_server.app,
                                 bindAddress=config._SOCKET_FILENAME,
                                 multithreaded=True,
                                 multiprocess=False,
                                 debug=config.debug)
        wsgi_server.run()
        plugin_manager.stop()
        del plugin_manager

        if not _reload:
            break


if __name__ == '__main__':
    main()
