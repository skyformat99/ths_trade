# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基于sqlalchemy的数据库组件，提供全局连接，配置管理，主从库支持，目前支持单主多从
"""
import random
import threading
from math import ceil

from sqlalchemy.engine import url
from sqlalchemy.orm import Query
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import engine_from_config

from tornado.util import import_object

from trest.config import settings
from ..logger import SysLogger
from ..exception import ConfigError
from ..storage import Storage
from ..utils.encrypter import aes_decrypt


__all__ = [
    'create_session',
    'DBConfigParser',
    'ConnBase',
    'SQLAlchemy',
    'get_connector',
    'Connector'
]

_SQLALCHEMY_PREFIX = 'sqlalchemy.'
_CONNECTION_TYPE = (
    'master',
    'slave',
)

_BASE_SQLALCHEMY_CONFIGURATION = {
    'sqlalchemy.connect_args': {
        'connect_timeout': 5,
    },
    'sqlalchemy.echo': False,
    'sqlalchemy.max_overflow': 10,
    'sqlalchemy.echo_pool': False,
    'sqlalchemy.pool_timeout': 30,
    'sqlalchemy.encoding': 'utf-8',
    'sqlalchemy.pool_size': 50,
    'sqlalchemy.poolclass': 'QueuePool'
}


def create_session(engine=None, scopefunc=None, twophase=False, **kwargs):
    def import_(param):
        if isinstance(param, str):
            return import_object(param)
        else:
            return param

    if scopefunc:
        scopefunc = import_(scopefunc)

    if 'extension' in kwargs:
        kwargs['extension'] = import_(kwargs['extension'])

    if 'class_' in kwargs:
        kwargs['class_'] = import_(kwargs['class_'])

    if 'query_cls' in kwargs:
        kwargs['query_cls'] = import_(kwargs['query_cls'])

    session = sessionmaker(autoflush=kwargs.pop('autoflush', True),
                           autocommit=kwargs.pop('autocommit', False),
                           expire_on_commit=kwargs.pop('expire_on_commit', True),
                           info=kwargs.pop('expire_on_commit', None),
                           **kwargs)

    if not twophase:
        session.configure(bind=engine)

    else:
        # eg:binds = {User:engine1, Account:engine2}
        session.configure(binds=engine, twophase=twophase)

    return scoped_session(session, scopefunc)


class DBConfigParser(object):
    @classmethod
    def parser_engines(cls):
        connections = settings.DATABASE_CONNECTION
        engines = {}
        for connection_name, connection_item in connections.items():
            if connection_name in engines:
                raise ConfigError('conn:%s ,has already exist.' % connection_name)

            engines[connection_name] = {
                'kwargs': connection_item.get('kwargs', {}),
                'master': [],
                'slaves': [],
            }

            connections_str = connection_item['connections']
            for conn in connections_str:
                # print("aes_decrypt", aes_decrypt(conn['PASSWD']))
                dburl = url.URL(drivername=conn['DRIVER'],
                    username=conn['UID'],
                    password=conn['PASSWD'],
                    # password=aes_decrypt(conn['PASSWD']),
                    host=conn['HOST'],
                    port=conn['PORT'],
                    database=conn['DATABASE'],
                    query=conn['QUERY'])
                if conn['ROLE'] == _CONNECTION_TYPE[0]:
                    engines[connection_name]['master'].append(dburl)
                elif conn['ROLE'] == _CONNECTION_TYPE[1]:
                    engines[connection_name]['slaves'].append(dburl)
                else:
                    raise ConfigError('role %s not allowed.' % conn['ROLE'])

            if not len(engines[connection_name]['master']):
                raise ConfigError('conn:%s ,master connection not found.' % connection_name)

        return engines

    @classmethod
    def parser_sqlalchemy_conf(cls):
        try:
            config = settings.sqlalchemy
        except Exception as ex:
            SysLogger.warning("sqlalchemy not found,using default sqlalchemy configuration")
            config = _BASE_SQLALCHEMY_CONFIGURATION

        poolclass_cfg = _SQLALCHEMY_PREFIX + 'poolclass'
        poolclass = config[poolclass_cfg] if poolclass_cfg in config else None
        # print("poolclass_cfg ", poolclass_cfg)
        if poolclass:
            config[poolclass_cfg] = import_object('sqlalchemy.pool.' + poolclass)
        return config


class _Connector(object):
    """
    创建连接
    """
    _conn_lock = threading.Lock()
    _conn = None

    def __init__(self, connection_class):
        self.class_ = connection_class

    @property
    def conn_pool(self):
        # 借用静态属性的单例模式
        if _Connector._conn:
            return _Connector._conn
        else:
            # 创建连接
            with _Connector._conn_lock:
                connection_pool = Storage()
                engines = DBConfigParser.parser_engines()
                config = DBConfigParser.parser_sqlalchemy_conf()
                try:
                    for name, engine in engines.items():
                        kw = engine['kwargs']
                        connection_pool[name] = self.class_(config,
                            master_url=engine['master'],
                            slaves_url=engine['slaves'],
                            session_conf=kw.pop('session', {}),
                            **kw)
                except Exception as e:
                    raise

            _Connector._conn = connection_pool
            return _Connector._conn

    def get_conn(self, conn_name):
        return self.conn_pool[conn_name]

    def get_session(self, connection_name='default'):
        session = self.get_conn(connection_name).session
        return session


class BaseQuery(Query):
    def paginate(self, page, per_page=20, default=None):
        """Returns `per_page` items from page `page`.
        Returns an :class:`Pagination` object.
        """
        page = int(page)
        per_page = int(per_page)
        if page < 1:
            return default
        items = self.limit(per_page).offset((page - 1) * per_page).all()
        if not items and page != 1:
            return default

        # No need to count if we're on the first page and there are fewer
        # items than we expected.
        if page == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = self.order_by(None).count()

        return Pagination(self, page, per_page, total, items)


class ConnBase(object):
    def __init__(self, config=None, master_url=None, slaves_url=None, session_conf=None, **kwargs):
        self.kwargs = kwargs or {}
        self.config = config or {}
        self.master_url = master_url
        self.slaves_url = slaves_url or []
        self.session_conf = session_conf or {}

    @property
    def engines(self):
        raise NotImplementedError

    @property
    def session(self):
        raise NotImplementedError

    def query(self, using_master=False):
        raise NotImplementedError

    def remove(self):
        """
        remove session to pool
        :return:
        """

    def ping_db(self):
        """
        ping db ,to prevent mysql sql gone away
        :return:
        """
        pass


class SQLAlchemy(ConnBase):
    def __init__(self, config=None, master_url=None, slaves_url=None, session_conf=None, **kwargs):

        """
        连接对象init
        :param base_conf: 全局配置，sqlalchemy.开头
        :param master_url: 主库连接
        :param slaves_url: 从库连接
        :param others_url: 其他类型，暂未实现
        :param kwargs: 自定义配置
        """
        super(SQLAlchemy, self).__init__(config=config,
            master_url=master_url,
            slaves_url=slaves_url,
            session_conf=session_conf,
            **kwargs)
        # 每一个engine都会有一个factory，感觉挺闹心，要是有10个engine。。就得10个factory，未来寻找一下全局只有一个factory的方案
        self._slave_tmp = None
        session_conf['query_cls'] = BaseQuery
        self._master_engine = engine_from_config(self.config, prefix=_SQLALCHEMY_PREFIX, url=master_url[0], **kwargs)
        self._master_session = create_session(self._master_engine, **session_conf)
        self._slaves_session = []
        self._slave_engine = []

        for slave in slaves_url:
            slave_engine = engine_from_config(self.config, prefix=_SQLALCHEMY_PREFIX, url=slave, **kwargs)
            self._slave_engine.append(slave_engine)
            self._slaves_session.append(create_session(slave_engine, **session_conf))

    def remove(self):
        # 连接释放通过可通过中间件提供，用户可自行决定是否要使用
        self._master_session.remove()
        if self._slaves_session:
            for slave in self._slaves_session:
                slave.remove()
        self._slave_tmp = None

    @property
    def session(self):
        return {
            'master': self.using_master_session(),
            'slave': self.using_slave_session()
        }

    def using_master_session(self):
        """
        主库session
        """
        return self._master_session

    @property
    def engines(self):
        return {
            'master': self._master_engine,
            'slaves': self._slave_engine
        }

    def using_slave_session(self):
        """
        从库session
        """
        if not self._slave_tmp:
            if self._slaves_session:
                self._slave_tmp = random.choice(self._slaves_session)
            else:
                self._slave_tmp = self._master_session

        return self._slave_tmp

    def query(self, using_master=False):
        if using_master:
            return self.using_master_session().query_property(BaseQuery)

        if self._slaves_session:
            return self.using_slave_session().query_property(BaseQuery)
        else:
            return self.using_master_session().query_property(BaseQuery)

    async def ping_db(self):
        # 防止数据库失联，定时ping一下
        ping = 'SELECT 0'
        try:
            self._master_session.execute(ping)
            self._master_session.remove()
            for slave in self._slaves_session:
                slave.execute(ping)
                slave.remove()
        except Exception as ex:
            # 由于目前没有使用mysql 这个地方在数据库连接失败后出现 定时ping一下的错误日志  现予以注释
            # SysLogger.error('ping mysql error:' + str(ex))
            pass

    def create_db(self):

        if not self._master_engine.echo:
            self._master_engine.echo = True
        Model.metadata.create_all(self._master_engine)

    def drop_db(self):
        if not self._master_engine.echo:
            self._master_engine.echo = True
        Model.metadata.drop_all(self._master_engine)


def get_connector(conn_class_):
    if issubclass(conn_class_, ConnBase):
        return _Connector(conn_class_)
    else:
        raise ConfigError('conn_class_ is wrong.')


class Pagination(object):
    """
    Internal helper class returned by :meth:`BaseQuery.paginate`.  You
    can also construct it from any other SQLAlchemy query object if you are
    working with other libraries.  Additionally it is possible to pass `None`
    as query object in which case the :meth:`prev` and :meth:`next` will
    no longer work.
    """

    def __init__(self, query, page, per_page, total, items):
        # : the unlimited query object that was used to create this
        # : pagination object.
        self.query = query
        # : the current page number (1 indexed)
        self.page = page
        # : the number of items to be displayed on a page.
        self.per_page = per_page
        # : the total number of items matching the query
        self.total = total
        # : the items for the current page
        self.items = items

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page - 1, self.per_page, error_out)

    @property
    def prev_num(self):
        """Number of the previous page."""
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page + 1, self.per_page, error_out)

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        This is how you could render such a pagination in the templates:

        .. sourcecode:: html+jinja

            {% macro render_pagination(pagination, endpoint) %}
              <div class=pagination>
              {%- for page in pagination.iter_pages() %}
                {% if page %}
                  {% if page != pagination.page %}
                    <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
                  {% else %}
                    <strong>{{ page }}</strong>
                  {% endif %}
                {% else %}
                  <span class=ellipsis>…</span>
                {% endif %}
              {%- endfor %}
              </div>
            {% endmacro %}
        """
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
                    (num > self.page - left_current - 1 and
                             num < self.page + right_current) or \
                            num > self.pages - right_edge:
                last_ = last + 1
                if last_ != num:
                    yield None
            yield num
            last = num

    def as_dict(self):
        return {
            "page": self.page,
            "per_page": self.per_page,
            "total": self.total,
            'items': [item.as_dict() for item in self.items],
        }

Connector = get_connector(SQLAlchemy)

