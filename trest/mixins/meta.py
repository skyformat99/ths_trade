#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict


class NoDupOrderedDict(OrderedDict):
    def __init__(self, clsname):
        self.clsname = clsname
        super().__init__()
        print('clsname ', clsname)

    def __setitem__(self, name, value):
        print('name ', type(name), name)
        print('value ', type(value), value)
        if name in self:
            raise TypeError('{} already defined in {}'.format(name, self.clsname))
        super().__setitem__(name, value)

class NoDupOrderedMeta(type):
    """防止重复的定义
        https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p14_capture_class_attribute_definition_order.html
    """
    def __new__(cls, clsname, bases, clsdict):
        d = dict(clsdict)
        d['_order'] = [name for name in clsdict if name[0] != '_']
        return type.__new__(cls, clsname, bases, d)

    @classmethod
    def __prepare__(cls, clsname, bases):
        return NoDupOrderedDict(clsname)
