#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
base handler
要获得中间件等特性需继承Handler
"""
import tornado.web
import tornado.locale
from raven.contrib.tornado import SentryMixin

from .config import settings
from .exception import Http404
from .exception import JsonError


class Handler(SentryMixin, tornado.web.RequestHandler):
    response_to_mq = False

    def params(self):
        return dict((k, self.get_argument(k)) for k, _ in self.request.arguments.items())

    def get_user_locale(self):
        lang = self.get_argument('lang', None)
        translation = settings.translation
        if translation:
            return tornado.locale.get(lang)
        # 默认中文
        return tornado.locale.get(settings.locale_default)

    def get_template_path(self):
        return f'applications/{self.app_name}/templates'

    def get_template_namespace(self):
        """Returns a dictionary to be used as the default template namespace.

        May be overridden by subclasses to add or modify values.

        The results of this method will be combined with additional
        defaults in the `tornado.template` module and keyword arguments
        to `render` or `render_string`.
        """
        namespace = super().get_template_namespace()
        namespace['lang'] = self.get_argument('lang', None)
        return namespace

    def error(self, msg='error', code=1, **args):
        self.set_status(200, msg)
        raise JsonError(code=code, msg=msg, **args)

    def success(self, msg='success', **args):
        self.set_status(200, msg)
        raise JsonError(code=200, msg=msg, **args)

class ErrorHandler(Handler):

    def _autoload_html(self, uri_li):
        uri_li = [i for i in uri_li if i]
        tmpl = '/' . join(uri_li[1:])
        params = {}
        self.render(tmpl, **params)

    def prepare(self):
        super(ErrorHandler, self).prepare()
        uri_li = self.request.uri.split('?', 1)[0].split('/')
        if uri_li[-1].endswith('.html'):
            return self._autoload_html(uri_li)
        raise Http404()


if settings.MIDDLEWARE_CLASSES:
    from .mixins.middleware import MiddlewareHandlerMixin

    Handler.__bases__ = (MiddlewareHandlerMixin,) + Handler.__bases__
