# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from flask import Flask
from importlib import import_module

logger = logging.getLogger(__name__)
app = Flask(__name__)

VERSION = 0.1


def load(configured_views):
    for view_name in configured_views:
        logger.info('Loading http view %s', view_name)
        module_name = 'xivo_dird.http_views.%s' % view_name
        import_module(module_name)
