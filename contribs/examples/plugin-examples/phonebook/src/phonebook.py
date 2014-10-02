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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer
from sqlalchemy.schema import Column
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import scoped_session

Base = declarative_base()
DB_URI = 'postgresql://asterisk:proformatique@localhost/asterisk'
Session = scoped_session(sessionmaker(bind=create_engine(DB_URI), autoflush=False, autocommit=True))

from xivo_dird.backends.directory_source_plugin import DirectorySourcePlugin
from xivo_dird.http import VERSION
from flask.globals import request
from flask.helpers import make_response

logger = logging.getLogger(__name__)


class PhonebookEntry(Base):

    __tablename__ = 'phonebook_entry'

    id = Column(Integer, nullable=False, primary_key=True)
    attributes = Column(HSTORE)


class PhonebookPlugin(DirectorySourcePlugin):

    def load(self, config=None):
        logger.debug('Loading with %s...', config)
        self._config = config

    def unload(self):
        self.session.close()

    def lookup(self, term, args):
        pattern = '%{term}%'.format(term=term)
        rows = Session().query(PhonebookEntry).filter(PhonebookEntry.attributes['name'].ilike(pattern)).all()
        return (self._attributes(row) for row in rows)

    def _attributes(self, row):
        attributes = {'id': row.id}
        attributes.update(row.attributes)
        return attributes

    def reverse_lookup(self, term):
        pass


def load(args=None):
    logger.info('loading')
    http_app = args['http_app']
    http_app.add_url_rule(
        '/{version}/directories/phonebook'.format(version=VERSION),
        view_func=phonebook_post,
        methods=['POST']
    )
    http_app.add_url_rule(
        '/{version}/directories/phonebook'.format(version=VERSION),
        view_func=phonebook_delete,
        methods=['DELETE']
    )


def phonebook_post():
    attributes = json.loads(request.data)
    entry = PhonebookEntry(attributes=attributes)
    session = Session()
    session.begin()
    session.add(entry)
    session.commit()
    return make_response('', 204, None, 'application/json')


def phonebook_delete():
    to_delete = json.loads(request.data)
    session = Session()
    session.begin()
    session.query(PhonebookEntry).filter(PhonebookEntry.id == to_delete['id']).delete()
    session.commit()
    return make_response('', 204, None, 'application/json')
