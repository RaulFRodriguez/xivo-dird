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

import json
import logging
import time

from flask import Flask, current_app, request
from flask.helpers import make_response
from xivo_dird.core import result_formatter

logger = logging.getLogger(__name__)
app = Flask(__name__)

VERSION = 0.1


@app.route('/{version}/directories/lookup/<profile>/headers'.format(version=VERSION))
def headers(profile):
    logger.info('profile {} headers'.format(profile))
    dummy = _encode_json(
        {'column_headers': ['Firstname', 'Lastname', 'Phone number'],
         'column_types': [None, None, 'office']}
    )
    return make_response(dummy, 200)


@app.route('/{version}/directories/lookup/<profile>'.format(version=VERSION))
def lookup(profile):
    logger.info('profile {} lookup'.format(profile))
    term = request.args['term']
    result = current_app.backend_plugin_manager.lookup(profile, term, request.args)
    formatted_result = result_formatter.format_lookup(result)
    return make_response(_encode_json(formatted_result), 200)


@app.route('/{version}/directories/reverse_lookup'.format(version=VERSION))
def reverse_lookup():
    logger.info('reverse lookup')

    if 'term' not in request.args:
        return make_response(_encode_json({'reasons': ['term is missing'],
                                           'timestamp': [time.time()],
                                           'status_code': 400}), 400)

    result = current_app.backend_plugin_manager.reverse_lookup(request.args['term'])
    formatted_result = result_formatter.format_reverse_lookup(result)
    return make_response(_encode_json(formatted_result), 200)


def _encode_json(data):
    return json.dumps(data, sort_keys=True, indent=4) + '\n'
