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

from flask import current_app, request
from flask.helpers import make_response
from xivo_dird.http import VERSION
from xivo_dird.core import result_formatter

logger = logging.getLogger(__name__)


aastra_search_answer = '''<AastraIPPhoneInputScreen type="string" editable="yes">
<Title><![CDATA[XiVO Search]]></Title>
<Prompt><![CDATA[Name or number:]]></Prompt>
<URL><![CDATA[http://10.37.0.254:80/service/ipbx/web_services.php/phonebook/search/]]></URL>
<Parameter>name</Parameter>
</AastraIPPhoneInputScreen>
'''


def lookup(profile):
    logger.info('profile {} lookup'.format(profile))
    if 'name' not in request.args:
        return make_response(aastra_search_answer, 200, None, 'text/xml')

    name = request.args['name']
    result = current_app.backend_plugin_manager.lookup(profile, name, args={})
    formatted_result = result_formatter.format_lookup(result)
    return make_response(_encode_xml(formatted_result), 200, None, 'text/xml')


def load(args=None):
    app = args['http_app']
    app.add_url_rule(
        '/{version}/directories/lookup/<profile>/aastra'.format(version=VERSION),
        'aastra_lookup',
        lookup,
    )


def _encode_xml(formatted_result):
    return '''<AastraIPPhoneTextMenu style="none" destroyOnExit="yes">
<MenuItem>
<Prompt><![CDATA[Carlos]]></Prompt>
<URI>Dial:<![CDATA[1003]]></URI>
<Dial><![CDATA[1003]]></Dial>
</MenuItem>
</AastraIPPhoneTextMenu>
'''
