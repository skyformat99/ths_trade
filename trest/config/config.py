#!/usr/bin/env python
# -*- coding: utf-8 -*-

document = """# f'{ROOT_PATH}/configs/{env}.yaml'
# 注意配置解析出来都是字符串，请不要带单引号或者双引号
# 例如 '0.0.0.0' "0.0.0.0" 都会报错


debug : true
xsrf_cookies : true
xheaders : true

arbitrary_ip : 0.0.0.0
port : 5080
local_ip : 127.0.0.1
translation : true
time_zone : Asia/Shanghai
language_code : zh-hans
cookie_secret : e921bfcd-ace4-4124-8657-c57a162365f6
login_pwd_rsa_encrypt : True
default_aes_secret : 883d65f06fd447f3a1e69a36e73f58e0
admin_session_key : de0b3fb0c2f44563944a8cccca7f225a
front_session_key : 171630947de24c969c28b2d178c4e0fe
valid_code_key : ab1195c6f0084b4f8b007d3aa7628a38
token_key : f30a2331813f46d0adc2bcf26fcbbbf4

INSTALLED_APPS :
    - admin

rabbitmq_config : ''
sentry_url :
config_cache_prefix : 'conf:'
user_cache_prefix : 'user:'
admin_cache_prefix : 'admin:'

# 超级管理员角色ID
SUPER_ROLE_ID : 1
DEFAULT_ROLE_ID : 2

# Super Admin 必须是 int 型数据
SUPER_ADMIN :
    - 1 # admin uid
    - 2 #

PASSWORD_HASHERS :
    # 第一个元素为默认加密方式
    - 'trest.utils.hasher.PBKDF2PasswordHasher'
    - 'trest.utils.hasher.PBKDF2SHA1PasswordHasher'

# 中间件     #
# ###########
MIDDLEWARE_CLASSES :
    - 'trest.middleware.dbalchemy.DBAlchemyMiddleware'
    - 'trest.middleware.AccessLogMiddleware'
    - 'trest.middleware.PushToMQMiddleware'

# sqlalchemy配置，列出部分，可自行根据sqlalchemy文档增加配置项
# 该配置项对所有连接全局共享
sqlalchemy :
    # (s秒)
    ping_db : 300
    # 每次取出ping多少个连接
    ping_conn_count : 5
    'sqlalchemy.connect_args' : {
        'connect_timeout' : 3
    }
    'sqlalchemy.echo' : false
    'sqlalchemy.max_overflow' : 10
    'sqlalchemy.echo_pool' : true
    'sqlalchemy.pool_timeout' : 5
    'sqlalchemy.encoding' : utf8
    'sqlalchemy.pool_size' : 5
    'sqlalchemy.pool_recycle' : 3600
    # 手动指定连接池类
    'sqlalchemy.poolclass' : QueuePool

# 数据库连接字符串，元祖，
# 每组为n个数据库连接，有且只有一个master，可配与不配slave
DATABASE_CONNECTION :
    default :
        connections :
        -
            ROLE: 'master'
            DRIVER : 'mysql+mysqldb'
            UID : root
            # 进过AES加密的密码，格式 aes::: + ciphertext
            PASSWD : 'eb27acWq#16E1'
            HOST : '127.0.0.1'
            PORT : 33061
            DATABASE : 'db_py_admin'
            QUERY : {'charset' : 'utf8mb4'}
        -
            ROLE : 'slave'
            DRIVER : 'mysql+mysqldb'
            UID : root
            # 进过AES加密的密码，格式 aes::: + ciphertext
            PASSWD : 'eb27acWq#16E1'
            HOST : '127.0.0.1'
            PORT : 33062
            DATABASE : 'db_py_admin'
            QUERY : {'charset' : 'utf8mb4'}

###########
# 缓存配置 #
###########

# default rediscache 其中之一
default_cache: 'default'

CACHES :
    'default':
        'BACKEND': 'trest.cache.backends.localcache.LocMemCache'
        'LOCATION': 'process_cache'
        'OPTIONS':
            'MAX_ENTRIES': 10000
            'CULL_FREQUENCY': 3

    'rediscache':
        'BACKEND': 'trest.cache.backends.rediscache.RedisCache'
        'LOCATION': '127.0.0.1:6379'
        'OPTIONS':
            'DB': 0
            'PASSWORD': 'abc123456'
            'PARSER_CLASS': 'redis.connection.DefaultParser'
            # 定时ping redis连接池，防止被服务端断开连接（s秒）
            'PING_INTERVAL': 120
            'POOL_KWARGS':
                'socket_timeout': 2
                'socket_connect_timeout': 2

# 配置模版引擎
# 引入相应的TemplateLoader即可
# 若使用自带的请留空
# 支持mako和jinja2
#       mako设置为 tornado.template.mako_loader.MakoTemplateLoader
#       jinj2设置为 tornado.template.jinja2_loader.Jinja2TemplateLoader
# 初始化参数请参照jinja的Environment或mako的TemplateLookup,不再详细给出
TEMPLATE_CFG :
    'template_engine': ''
    # 模版路径由tornado.handler中commonhandler重写，
    # 无需指定，模版将存在于每个应用的根目录下
    #通用选项
    'filesystem_checks': True
    'cache_directory': '../_tmpl_cache'  # 模版编译文件目录,通用选项
     # 暂存入内存的模版项，可以提高性能，mako选项,详情见mako文档
    'collection_size': 50
    # 类似于mako的collection_size，设定为-1为不清理缓存，0则每次都会重编译模板
    'cache_size': 0
    # 格式化异常输出，mako专用
    'format_exceptions': False
    # 默认转义设定，jinja2专用
    'autoescape': False

# tornado日志功能配置
# Logging中有
# NOTSET < DEBUG < INFO < WARNING < ERROR < CRITICAL 这几种级别，
# 日志会记录设置级别以上的日志
# when  时间  按照哪种时间单位滚动（可选s-按秒，m-按分钟，h-按小时，d-按天，w0-w6-按指定的星期几，midnight-在午夜）
log_cfg:
    log_dir: ''
    standard_format : &standard_format '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d] [%(levelname)s][%(message)s]'

    logging :
        -
            'name': 'access_log'
            'log_to_stderr': True
            'filename': 'access_log.log'
        -
            'name': 'tornado.debug.log'
            'level': 'DEBUG'
            'log_to_stderr': True
            'when': 'w0'
            'interval': 1
            'formatter': *standard_format
            'filename': 'debug_log.log'
        -
            'name': 'tornado.info.log'
            'level': 'INFO'
            'log_to_stderr': True
            'when': 'midnight'
            'interval': 1
            'formatter': *standard_format
            'filename': 'info_log.log'
        -
            'name': 'tornado.warning.log'
            'level': 'WARNING'
            'log_to_stderr': True
            'when': 'midnight'
            'interval': 1
            'formatter': *standard_format
            'filename': 'warning_log.log'
        -
            'name': 'tornado.error.log'
            'level': 'ERROR'
            'log_to_stderr': True
            'when': 'midnight'
            'interval': 1
            'formatter': *standard_format
            'filename': 'error_log.log'
        -
            'name': 'tornado.critical.log'
            'level': 'CRITICAL'
            'log_to_stderr': True
            'when': 'midnight'
            'interval': 1
            'formatter': *standard_format
            'filename': 'critical_log.log'

email :
    from_name :
    from_addr :
    smtp_sever :
    smtp_port :
    auth_code :
"""
