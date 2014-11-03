# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import logging

from time import time
from xivo_dird import BaseViewPlugin
from flask import jsonify
from flask_restplus import Resource

logger = logging.getLogger(__name__)


class HeadersViewPlugin(BaseViewPlugin):

    def load(self, args):
        api_class = make_api_class(args['config'],
                                   args['http_namespace'],
                                   args['rest_api'])
        args['http_namespace'].route('/lookup/<profile>/headers')(api_class)


def make_api_class(config, namespace, api):

    class Headers(Resource):

        def get(self, profile):
            logger.debug('header request on profile %s', profile)
            try:
                display_name = config.get('profile_to_display', {})[profile]
                display_configuration = config.get('displays', {})[display_name]
            except KeyError:
                logger.warning('profile %s does not exist, or associated display does not exist', profile)
                error = {
                    'reason': ['The lookup profile does not exist'],
                    'timestamp': [time()],
                    'status_code': 404,
                }
                return jsonify(error), 404

            response = {'column_headers': [column.get('title') for column in display_configuration],
                        'column_types': [column.get('type') for column in display_configuration]}
            return jsonify(response)

    return Headers
