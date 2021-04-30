#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import redis
import datetime
from decimal import Decimal
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from trest.utils import utime
from .dbalchemy import Connector
from .dbalchemy import Query


MetaBaseModel = declarative_base()

class Model(MetaBaseModel):
    """
    """
    __abstract__ = True
    __tablename__ = ''
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    __connection_name__ = 'default'

    @declared_attr
    def Q(cls) -> Query:
        """ not using master """
        return Connector.get_conn(cls.__connection_name__).query()

    @declared_attr
    def Update(cls) -> Query:
        """ using master """
        return Connector.get_conn(cls.__connection_name__).query(True)

    @declared_attr
    def session(cls):
        """ using master """
        return Connector.get_session(cls.__connection_name__)['master']

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def as_dict(self, fields = []):
        """ 模型转换为字典 """
        items = {}
        _no_str_tuple = (datetime.datetime, datetime.date, Decimal)
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            val = '' if val is None else val
            if isinstance(val, _no_str_tuple):
                val = str(val)
            if type(fields) == list and len(fields) > 0:
                if column.name in fields:
                    items[column.name] = val
            else :
                items[column.name] = val
        return items
