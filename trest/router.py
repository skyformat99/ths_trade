#!/usr/bin/env python
# -*- coding: utf-8  -*-
import os
import six
import inspect
import importlib
import functools


from .config import settings
from .utils.func import md5


def _get_modules(package="."):
    """
    获取包名下所有非__init__的模块名
    """
    modules = []
    files = os.listdir(package)
    for file in files:
        if file.startswith(('_', '.')):
            continue
        if not file.endswith('.py'):
            continue
        name, ext = os.path.splitext(file)
        if name in ['common',]:
            continue
        modules.append('.' + name)
    return modules

def _get_handler_params(module, attr):
    """
    获取module下面的所有参数
    """
    if attr.startswith('_'):
        return (False, False)
    if not attr.endswith('Handler'):
        return (False, False)
    if attr in ['Handler', 'CommonHandler']:
        return (False, False)
    handler = getattr(module, attr)
    params = inspect.getmembers(handler, lambda f: callable(f) and hasattr(f, '_path'))
    if not params:
        return (False, False)
    return (handler, params)

def _check_path(check_param):
    """
    给参数按照path/method分组api
    """
    app_name = check_param['app_name']
    path = check_param['path']
    val = check_param['val']
    name = check_param['name']
    method_path_set = check_param['method_path_set']
    path_method_dict = check_param['path_method_dict']
    method = val._method.lower()

    if method != 'get' and type(val._path) == list:
        raise Exception(f'only the get method supported list path')
    if type(path) != str:
        raise Exception(f'path({path}) type only supported str, but it is {type(path)}')
    path = path if path.startswith('/') else rf'/{app_name}/{path}'

    if path not in path_method_dict.keys():
        path_method_dict[path] = {}
    method_path = f'{method}:{path}'
    if method_path in method_path_set:
        raise Exception(f'api repeated {method_path}')
    path_method_dict[path][method] = (path, val, name)
    method_path_set.add(method_path)
    return (method_path_set, path_method_dict)

def _get_path_method(app_name, params):
    """
    给参数按照path/method分组api，便于 _create_handlers/3创建class，一个GET API支出多个path
    """
    path_method_dict = {}
    method_path_set = set()
    for name, val in params:
        if type(val._path) == list:
            for path in val._path:
                check_param = {}
                check_param['app_name'] = app_name
                check_param['path'] = path
                check_param['val'] = val
                check_param['name'] = name
                check_param['method_path_set'] = method_path_set
                check_param['path_method_dict'] = path_method_dict
                (method_path_set, path_method_dict) = _check_path(check_param)
        else:
            check_param = {}
            check_param['app_name'] = app_name
            check_param['path'] = val._path
            check_param['val'] = val
            check_param['name'] = name
            check_param['method_path_set'] = method_path_set
            check_param['path_method_dict'] = path_method_dict
            (method_path_set, path_method_dict) = _check_path(check_param)
    return path_method_dict

def _create_handlers(app_name, handler, package, path_method_dict):
    handlers = []
    not_get = ['head', 'post', 'delete', 'patch', 'put', 'options']
    for (path, dt2) in path_method_dict.items():
        intersection = set(not_get) & set(dt2.keys())
        if not intersection :
            classname = f'Handler{md5(path)}'
            new_class = type(classname, (handler,), {})
            new_class.__module__ = handler.__module__
        else:
            new_class = handler
        # end if
        setattr(new_class, 'app_name', app_name)
        for (method2, (path2, val2, name2)) in dt2.items():
            setattr(new_class, method2, val2)

        for (_, (path2, _, name2)) in dt2.items():
            handlers.append((path2, new_class, {'name':name2}))

    return handlers

def get_handlers(app_name):
    """ 自动加载特定APP里面的handler """
    namespace = f'{settings.ROOT_PATH}/applications/{app_name}/handlers/'
    modules = _get_modules(namespace)
    # 将包下的所有模块，逐个导入，并调用其中的函数
    package = f'applications.{app_name}.handlers'
    handlers = []
    for module in modules:
        try:
            module = importlib.import_module(module, package)
        except Exception as e:
            raise e
        for attr in dir(module):
            (handler, params) = _get_handler_params(module, attr)
            if not params:
                continue
            path_method_dict = _get_path_method(app_name, params)
            handlers += _create_handlers(app_name, handler, package, path_method_dict)
    return handlers

def get(*dargs, **dkargs):
    """
    """
    def wrapper(method):
        path = dargs[0]
        print(path)
        @functools.wraps(method)
        def _wrapper(*args, **kargs):
            return method(*args, **kargs)
        _wrapper._path = path
        _wrapper._method = 'get'
        return _wrapper
    return wrapper

def head(*dargs, **dkargs):
    """
    """
    def wrapper(method):
        path = dargs[0]
        @functools.wraps(method)
        def _wrapper(*args, **kargs):
            return method(*args, **kargs)
        _wrapper._path = path
        _wrapper._method = 'head'
        return _wrapper
    return wrapper

def post(*dargs, **dkargs):
    """
    """
    def wrapper(method):
        path = dargs[0]

        @functools.wraps(method)
        def _wrapper(*args, **kargs):
            return method(*args, **kargs)
        _wrapper._path = path
        _wrapper._method = 'post'
        return _wrapper
    return wrapper

def delete(*dargs, **dkargs):
    """
    """
    def wrapper(method):
        path = dargs[0]
        @functools.wraps(method)
        def _wrapper(*args, **kargs):
            return method(*args, **kargs)
        _wrapper._path = path
        _wrapper._method = 'delete'
        return _wrapper
    return wrapper

def patch(*dargs, **dkargs):
    """
    """
    def wrapper(method):
        path = dargs[0]
        @functools.wraps(method)
        def _wrapper(*args, **kargs):
            return method(*args, **kargs)
        _wrapper._path = path
        _wrapper._method = 'patch'
        return _wrapper
    return wrapper

def put(*dargs, **dkargs):
    """
    """
    def wrapper(method):
        path = dargs[0]
        @functools.wraps(method)
        def _wrapper(*args, **kargs):
            return method(*args, **kargs)
        _wrapper._path = path
        _wrapper._method = 'put'
        return _wrapper
    return wrapper

def options(*dargs, **dkargs):
    """
    """
    def wrapper(method):
        path = dargs[0]
        @functools.wraps(method)
        def _wrapper(*args, **kargs):
            return method(*args, **kargs)
        _wrapper._path = path
        _wrapper._method = 'options'
        return _wrapper
    return wrapper
