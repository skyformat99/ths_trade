#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""URL处理器
[description]
"""
from tornado.escape import json_decode
from trest.handler import Handler



class CommonHandler(Handler):
    format = 'json'
    _postdata = None
    _myshopid = None
    _update = False

    def prepare(self):
        self.params()

    def params(self) -> None:
        # 只有post方法 进行参数解析，其它不处理
        try:
            if (self.request.method.lower() == 'post'):
                if ((self.request.files != None) and (len(self.request.files) > 0)):
                    self._postdata = dict((k, self.get_argument(k)) for k, _ in self.request.arguments.items())
                else:
                    self._postdata = json_decode(self.request.body)
                if ('bizID' in self._postdata):
                    self._myshopid = self._postdata['bizID']
                if ('isUpdate' in self._postdata):
                    self._update = self._postdata['isUpdate'] == 1
        except Exception as e:
            print(e)

    # 失败的返回方法
    def isBag(self, errormsg):
        return self.error(msg=errormsg, code=300)

    # 成功的返回方法
    def isOk(self, info):
        return self.success(data=info)

    # 对记录集的返回，自动判断，如果有返回成功，没有返回失败
    def isBack(self, info):
        if (info == None):
            return self.isOk(info)
        else:
            return self.isBag('服务器响应失败！')

    # 对需要返回记录集的接口的调用方法
    def isResBack(self, info):
        if (info == None):
            return self.isBag('服务器处理失败！')
        else:
            return self.isOk(info)
