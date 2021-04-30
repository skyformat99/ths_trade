
from common.CommonHandler import CommonHandler
from trest.router import post
import json
import pandas as pd
from pandas.io.json import json_normalize
import applications.Global_Var_Model as gl
import applications.trade.Search_Work_Log as SearchWorkLog
import uuid
import time
from applications import API_Config


def InputQueue(_json):
    """ 输入一个dataframe 加入队列中 """
    data_list = json.loads(_json)  # 字符串转json
    if isinstance(data_list,str):
        data_list = json.loads(data_list)

    for item in data_list:
        item["stock_no"] = str(item["code"]).split('.')[0]
        item["stock_name"] = str(item["name"])
        item["amount"] = str(item["ct_amount"])
        item["key"] = str(uuid.uuid1())
        item["status"] = 0

    df_1 = json_normalize(data_list)  # json转换dataframe
    df_1.head()
    df = df_1.loc[:, API_Config.cfg['activework_field']]  # 获取csv 指定列
    # 接收到新的指令时加入到dataframe中 并存储一份
    gl.gl_queue_DF_Data = pd.concat([gl.gl_queue_DF_Data, df])  # 连接两个dataframe
    gl.gl_queue_DF_Data = gl.gl_queue_DF_Data.loc[:, API_Config.cfg['activework_field']]  # 连接后指定列
    gl.gl_queue_DF_Data = gl.gl_queue_DF_Data.reset_index(drop=True)  # 重建索引
    gl.gl_queue_DF_Data = gl.gl_queue_DF_Data.loc[:, API_Config.cfg['activework_field']]  # 取值列保存到csv
    gl.gl_queue_DF_Data.to_csv(API_Config.cfg['activework_path'], sep='\t')

def SearchData(_json):

    """ 查询结果 """
    i = 0
    # 检测是否再干活 如果在干活则等待0.5秒  共等待300次
    while i <= 300:
        if gl.gl_is_working:
            time.sleep(API_Config.cfg["sleepB"])
        else:
            gl.gl_is_working = True  # 设置自动化交易正在进行中
            gl.gl_is_searching = True  # 设定查询中的全局变量正在工作
            # 接收到新的指令时加入到dataframe中 并存储一份
            item = json.loads(_json)  # 字符串转json
            # 传入的策略号返回数据集
            df = SearchWorkLog.searchWorkLog(item)
            resJSON = df.to_dict('records')
            # 返回结果集
            # resJSON = {'fff': 'aaaa', 'name': 'bb'}
            i = 1000
        i += 1
    gl.gl_is_working = False  # 干完活设置空闲状态
    gl.gl_is_searching = False  # 设定查询中的全局变量正在工作
    return resJSON
