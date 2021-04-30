#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import yaml
from tornado.options import options

from .config import document
from ..storage import dict_to_storage
from ..exception import ConfigError


# 检查全局变量 ROOT_PATH 设置
if hasattr(options, 'ROOT_PATH') and os.path.exists(options.ROOT_PATH):
    ROOT_PATH = options.ROOT_PATH
else:
    raise ConfigError('ROOT_PATH is not configured')

env = os.getenv('RUNTIME_ENV')
if not env:
    # f'{ROOT_PATH}/.env'
    fpath = os.path.join(ROOT_PATH,'local.env')
    with open(fpath, encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    env = cfg.get('RUNTIME_ENV','')

# 检查系统环境变量 RUNTIME_ENV 设置
if env not in ['local', 'dev', 'test', 'product']:
    msg = f'The system variable RUNTIME_ENV ({env}) is not one of the local, dev, test, or product'
    raise ConfigError(msg)

# _yf = f'{ROOT_PATH}/configs/{env}.yaml'
_yf = os.path.join(ROOT_PATH,'configs',env + '.yaml')
if not(os.path.isfile(_yf) and os.access(_yf, os.R_OK)):
    raise ConfigError(f'The ENV file({_yf}) does not exist or is unreadable')

with open(_yf, encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

_default_cfg = yaml.safe_load(document)
_default_cfg.update(cfg)

settings = dict_to_storage(_default_cfg)

settings.ROOT_PATH = ROOT_PATH
settings.STATIC_PATH = os.path.join(ROOT_PATH, 'statics')
settings.ENV = env


settings.locale_default = 'zh_CN'
# 是否开启国际化
# settings.translation == True 是有效
if not settings.get('translations_dir'):
    settings['translations_dir'] = os.path.join(ROOT_PATH, 'datas/locales')

# tornado全局配置
settings.TORNADO_CONF = {
    'xsrf_cookies': settings.xsrf_cookies,
    'login_url': '/admin/login',
    'cookie_secret': settings.cookie_secret,
    # 'ui_modules': ui_modules,
    'template_path': os.path.join(ROOT_PATH, 'applications/admin/templates'),
    'static_path': settings.STATIC_PATH,
    # 安全起见，可以定期生成新的cookie 秘钥，生成方法：
    # base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
}

# 系统角色，非超级管理员不允许编辑权限和删除
settings.SYS_ROLE = [
    settings.SUPER_ROLE_ID,
    settings.DEFAULT_ROLE_ID,
]

log_dir = settings.log_cfg.log_dir
settings.LOGGING_DIR = log_dir if log_dir else os.path.join(ROOT_PATH, 'logs/')
