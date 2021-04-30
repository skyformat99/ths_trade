#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from tornado.options import define

abs_file = os.path.abspath(sys.argv[0])
ROOT_PATH = abs_file[:abs_file.rfind(os.path.sep)]
define('ROOT_PATH', ROOT_PATH)

sys.path.insert(0, '/trest')
# 把当前目录添加到 sys.path 开头
sys.path.insert(0, ROOT_PATH)

from trest.webserver import run
import applications.Timer_Exec_Trade

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)
