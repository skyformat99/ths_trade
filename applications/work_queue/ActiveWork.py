import pandas as pd
import  applications.Global_Var_Model as gl
import sys
sys.path.append(r'..')
from applications import API_Config


class ActiveWork():
    def __init__(self):
        """ 进入动态的工作流 首先检测ActiveWork是否有未作完的 如果有取出赋值 并等待下次的timer的取执  """
        if gl.gl_queue_DF_Data is None:
            gl.gl_queue_DF_Data = pd.read_csv(API_Config.cfg["activework_path"], sep='\t')
            print("ActiveWork的初始化值是:", gl.gl_queue_DF_Data)

    def get_Queue_the_one(self):
        """ 获取队列中的未执行的一条数据顺序获取 """
        # 由timer 定时取
        # 如果空闲则获取第一条未做的数据
        # 判断当前数据集中是否存在数据

        if (gl.gl_queue_DF_Data is None) | gl.gl_queue_DF_Data.empty:
            return None
        else:
            # 如果空闲 则返回未执行的第一条数据返回 进行工作
            df_where = gl.gl_queue_DF_Data[gl.gl_queue_DF_Data['status'] == 0]
            if df_where.empty:
                return None
            else:
                return df_where.iloc[0]

    def edit_queue_the_one_status(self, key, path=API_Config.cfg["activework_path"]):
        """ 修改队列中的一条状态 修改后保存一份ActiveWork """
        # 修改状态为已做
        # gl.gl_queue_DF_Data.loc[gl.gl_queue_DF_Data['status'] == 0, 'status'] = 1
        gl.gl_queue_DF_Data.loc[(gl.gl_queue_DF_Data['key'] == str(key)), 'status'] = 1
        field = ["key", "strategy_no", "stock_no", "stock_name","amount", "operate", "status"]
        gl.gl_queue_DF_Data = gl.gl_queue_DF_Data.loc[:, field]  # 取值列保存到csv
        # 状态发生改变保存一份csv
        gl.gl_queue_DF_Data.to_csv(path, sep='\t') # './applications/tool/ActiveWork.csv'
        # return gl.gl_queue_DF_Data;
