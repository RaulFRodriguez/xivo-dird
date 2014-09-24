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
import json
import time

from flask.helpers import make_response
from xivo_dird.core import result_formatter
from xivo_dird.http import VERSION
from flask import current_app, request


logger = logging.getLogger(__name__)


def headers(profile):
    logger.info('profile {} headers'.format(profile))
    dummy = _encode_json(
        {'column_headers': ['Firstname', 'Lastname', 'Phone number'],
         'column_types': [None, None, 'office']}
    )
    return make_response(dummy, 200, None, 'application/json')


def lookup(profile):
    logger.info('profile {} lookup'.format(profile))
    term = request.args['term']
    result = current_app.backend_plugin_manager.lookup(profile, term, request.args)
    logger.debug('Lookup result: %s', result)
    formatted_result = result_formatter.format_lookup(result)
    return make_response(_encode_json(formatted_result), 200, None, 'application/json')


def reverse_lookup():
    logger.info('reverse lookup')

    if 'term' not in request.args:
        return make_response(_encode_json({'reasons': ['term is missing'],
                                           'timestamp': [time.time()],
                                           'status_code': 400}), 400)

    result = current_app.backend_plugin_manager.reverse_lookup(request.args['term'])
    formatted_result = result_formatter.format_reverse_lookup(result)
    return make_response(_encode_json(formatted_result), 200, None, 'application/json')


def load(args=None):
    http_app = args['http_app']
    http_app.add_url_rule(
        '/{version}/directories/lookup/<profile>/headers'.format(version=VERSION),
        'default_header',
        headers,
    )
    http_app.add_url_rule(
        '/{version}/directories/lookup/<profile>'.format(version=VERSION),
        __name__,
        lookup,
    )
    http_app.add_url_rule(
        '/{version}/directories/reverse_lookup'.format(version=VERSION),
        'default_reverse',
        reverse_lookup,
    )


def _encode_json(data):
    return json.dumps(data, sort_keys=True, indent=4) + '\n'
