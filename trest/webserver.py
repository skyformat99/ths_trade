#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import logging
import asyncio
import warnings
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver

from tornado.options import options
from tornado.options import OptionParser
from tornado.options import parse_command_line
from tornado.options import add_parse_callback
from tornado.util import import_object
from tornado.routing import Rule
from tornado.routing import RuleRouter
from tornado.routing import PathMatches
from tornado.log import LogFormatter
from tornado.log import define_logging_options

from raven.contrib.tornado import AsyncSentryClient

from .config import settings
from .exception import ConfigError
from .application import Application
from .router import get_handlers
from .logger import enable_pretty_logging

import importlib
importlib.reload(sys)


class Server(object):
    start_time = None

    def __init__(self, ioloop=None):
        self.httpserver = None
        self.router = None
        self.ioloop = ioloop

    def _tornado_conf(self):
        tornado_conf = settings.TORNADO_CONF
        if 'default_handler_class' in tornado_conf and \
                isinstance(tornado_conf['default_handler_class'], str):
            tornado_conf['default_handler_class'] = import_object(tornado_conf['default_handler_class'])
        else:
            tornado_conf['default_handler_class'] = import_object('trest.handler.ErrorHandler')

        if hasattr(options, 'template_path') and os.path.exists(options.template_path):
            tornado_conf['template_path'] = options.template_path

        if hasattr(options, 'static_path') and os.path.exists(options.static_path):
            tornado_conf['static_path'] = options.static_path

        if hasattr(options, 'login_url') and os.path.exists(options.login_url):
            tornado_conf['login_url'] = options.login_url

        tornado_conf['debug'] = settings.debug
        tornado_conf['xsrf_cookies'] = settings.xsrf_cookies
        return tornado_conf

    def _install_application(self, handlers):
        tornado_conf = self._tornado_conf()
        app_obj = Application(handlers=handlers,
             default_host='',
             transforms=None, wsgi=False,
             middlewares=settings.MIDDLEWARE_CLASSES,
             **tornado_conf)
        app_obj.sentry_client = AsyncSentryClient(
            settings.get('sentry_url', '')
        )
        return app_obj

    def _load_application(self):
        """
        """
        if settings.translation:
            try:
                from tornado import locale
                locale.load_translations(settings.translations_dir)
            except:
                warnings.warn('locale dir load failure,maybe your config file is not set correctly.')

        apps = settings.INSTALLED_APPS
        if not apps:
            raise ConfigError('settings.INSTALLED_APPS is empty')
        handlers = []
        for app_name in apps:
            handlers += get_handlers(app_name)
        app = self._install_application(handlers)
        self.router = RuleRouter([Rule(PathMatches('/.*'), app)])

    def _load_httpserver(self, sockets=None, **kwargs):
        if not sockets:
            from tornado.netutil import bind_sockets
            sockets = bind_sockets(options.port, options.address)

        if not kwargs.get('xheaders', None):
            kwargs['xheaders'] = settings.xheaders

        self.http_server = tornado.httpserver.HTTPServer(
            self.router, **kwargs)

        self.http_server.add_sockets(sockets)
        return self.httpserver

    def load_all(self, sockets=None, **kwargs):
        self._parse_command()
        self._load_application()
        if not self.httpserver:
            self._load_httpserver(sockets, **kwargs)

    def start(self):
        self._print_settings_info()
        if not self.ioloop:
            self.ioloop = asyncio.get_event_loop()
        if self.http_server:
            self.http_server.start()
        print(f'starting use time: {time.time() - self.start_time} second')
        self.ioloop.run_forever().start()

    def _print_settings_info(self):
        if settings.debug:
            print('tornado version: %s' % tornado.version)
            print('locale support: %s' % settings.get('translation', False))
            print('load apps:')
            for app in settings.INSTALLED_APPS:
                print(' - %s' % str(app))
            print('template engine: %s' % (settings.TEMPLATE_CFG.template_engine or 'default'))
            print('server started. development server at http://%s:%s/' % (options.address, options.port))

    def _parse_command(self, args=None, final=False):
        """
        解析命令行参数，解析logger配置
        :return:
        """
        self._define()
        add_parse_callback(self._parse_logger_callback)
        parse_command_line(args, final)
        options.run_parse_callbacks()

    def _parse_logger_callback(self):
        # print('parse_logger_callback: ')
        if options.disable_log:
            options.logging = None
        if options.log_file_prefix and options.log_port_prefix:
            options.log_file_prefix += ".%s" % options.port

        tornado_logger = logging.getLogger('tornado')
        enable_pretty_logging(logger=tornado_logger)
        logdir = options.logging_dir or settings.LOGGING_DIR
        for log in settings.log_cfg.logging:
            opt = OptionParser()
            define_logging_options(opt)
            self._define(opt)
            opt.log_rotate_when = log.get('when', 'midnight')
            opt.log_to_stderr = log.get('log_to_stderr', False) if options.log_to_stderr is None else options.log_to_stderr
            opt.logging = log.get('level', 'INFO')
            opt.log_file_prefix = os.path.join(logdir, log['filename'])
            if log.get('backups'):
                opt.log_file_num_backups = log.get('backups')
            if opt.log_port_prefix:
                opt.log_file_prefix += ".%s" % options.port
            opt.log_rotate_interval = log.get('interval', 1)
            opt.log_rotate_mode = 'time'
            logger = logging.getLogger(log['name'])
            logger.propagate = 0
            enable_pretty_logging(options=opt, logger=logger)

            map(lambda h: h.setFormatter(
                LogFormatter(
                    fmt=log.get("formatter", settings.standard_format),
                    color=settings.DEBUG
                )
            ), logger.handlers)

    def _define(self, options=options):
        """
        定义命令行参数,你可以自定义很多自己的命令行参数，或重写此方法覆盖默认参数
        :return:
        """
        try:
            # 增加timerotating日志配置
            options.define("log_rotate_when", type=str, default='midnight',
                           help=("specify the type of TimedRotatingFileHandler interval "
                                 "other options:('S', 'M', 'H', 'D', 'W0'-'W6')"))
            options.define("log_rotate_interval", type=int, default=1,
                           help="The interval value of timed rotating")

            options.define("log_rotate_mode", type=str, default='time',
                           help="The mode of rotating files(time or size)")
        except:
            pass

        address = settings.arbitrary_ip
        options.define("port", default=settings.port, help="run server on it", type=int)
        options.define("settings", default='', help="setting module name", type=str)
        options.define("address", default=address, help=f'listen host,default:{address}', type=str)
        options.define("log_patch", default=True,
                       help='Use ProcessTimedRotatingFileHandler instead of the default TimedRotatingFileHandler.',
                       type=bool)
        options.define("log_port_prefix", default=None, help='add port to log file prefix.', type=bool)
        options.define("logging_dir", default='', help='custom log dir.')
        options.define("disable_log", default=True, help='disable tornado log function.')


def run(sockets=None, **kwargs):
    start_time = time.time()
    ioloop = asyncio.get_event_loop()
    server = Server(ioloop=ioloop)
    server.start_time = start_time
    server.load_all(sockets, **kwargs)
    server.start()
    return server
