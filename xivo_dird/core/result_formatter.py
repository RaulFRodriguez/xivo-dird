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

import json
import logging

logger = logging.getLogger(__name__)


def format_reverse_lookup(result):
    result = {
        'name': result.result,
        'number': result.query,
        'source': result.source,
    }
    return json.dumps(result)


def format_lookup(source_results):
    result = []
    for source_result in source_results:
        for entry in source_result.results:
            result.append(
                {
                    'column_values': entry,
                    'source': source_result.source,
                }
            )
    return json.dumps(result)
