from threading import Timer
from applications.work_queue.ActiveWork import ActiveWork
import applications.Global_Var_Model as gl
import datetime
import time
import applications.trade.Exec_Auto_Trade as ExecAutoTrade
from applications.tool.CSV_Helper import CSVHelper
import sys
sys.path.append(r'')
from applications import API_Config

# 活动的工作流初始化
aw = ActiveWork()
pdcsv = CSVHelper()

def search_item_exec():
    """ 查询是否有任务 如果有则执行 执行完再次进入查询任务并执行 直到所有的任务做完 """
    item = aw.get_Queue_the_one()
    if item is not None:
        # 如果不是空则开始执行
        ExecAutoTrade.exec_run(item)
        aw.edit_queue_the_one_status(item['key'])
        # 有任务就执行 直到队列中所有的都干完
        search_item_exec()

    else:
        # 没有任务可做 则返回空闲 定时器开始正常执行
        gl.gl_is_working = False
        # 先查询是否有未从委托中获取数据同步work_data_log  判断依据: data["委托时间"] = ""    data["成交数量"] = -1    data["委托价格"] = -1   data["成交均价"] = -1  data["撤消数量"] = -1

        df = pdcsv.getCVS()
        df = df.astype({'合同编号': 'str'})
        df_where = df[(df['成交数量'] == -1) & (df['合同编号'] != '0')]
        if df_where.empty:
            pass
        else:
            # 设定查询中
            gl.gl_is_searching = True
            # 如果有则去查询委托数据集
            item = {
                "operate": "get_today_entrusts",
            }
            grid = ExecAutoTrade.exec_run(item)
            grid = grid.astype({'合同编号': 'str'})
            # 根据查询到的数据 循环进行比对合同号匹配
            for idx, dfrowitem in df.iterrows():
                for jdx, gridrowitem in grid.iterrows():
                    # 把数据填充上
                    if dfrowitem['合同编号'] == gridrowitem['合同编号']:
                        df.loc[df['合同编号'] == gridrowitem['合同编号'], '委托时间'] = gridrowitem['委托时间']
                        df.loc[df['合同编号'] == gridrowitem['合同编号'], '证券代码'] = gridrowitem['证券代码']
                        df.loc[df['合同编号'] == gridrowitem['合同编号'], '证券名称'] = gridrowitem['证券名称']
                        df.loc[df['合同编号'] == gridrowitem['合同编号'], '操作'] = gridrowitem['操作']
                        df.loc[df['合同编号'] == gridrowitem['合同编号'], '备注'] = gridrowitem['备注']
                        df.loc[df['合同编号'] == gridrowitem['合同编号'], '委托数量'] = gridrowitem['委托数量']
                        df.loc[df['合同编号'] == gridrowitem['合同编号'], '成交数量'] = gridrowitem['成交数量']
                        df.loc[df['合同编号'] == gridrowitem['合同编号'], '委托价格'] = gridrowitem['委托价格']
                        df.loc[df['合同编号'] == gridrowitem['合同编号'], '成交均价'] = gridrowitem['成交均价']
                        df.loc[df['合同编号'] == gridrowitem['合同编号'], '撤消数量'] = gridrowitem['撤消数量']
            # 保存work_data_log.csv
            pdcsv.saveCSV(df)  # 写入新的dataframe 到csv
            gl.gl_is_searching = False

def auto_trade(interval):
    """ 执行自动化交易 定时去dataframe获取数据 """
    if gl.gl_is_searching:
        print("====" + str(datetime.datetime.now().strftime("%H:%M:%S")) + "  查询中====")
        pass
    else:
        # 如果已经再工作中则不做任何处理
        if gl.gl_is_working:
            return

        gl.gl_is_working = True
        # 获取队列中的一条数据
        search_item_exec()
        # print("====" + str(datetime.datetime.now().strftime("%H:%M:%S")) + "  空闲====")

    # 判断时间进行清空csv 每天凌晨清除
    time_start = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '00:00', '%Y-%m-%d%H:%M')
    time_end = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '00:03', '%Y-%m-%d%H:%M')
    n_time = datetime.datetime.now()
    # 判断当前时间是否在范围时间内
    if n_time > time_start and n_time < time_end:
        # 清空Activework
        gl.gl_queue_DF_Data.drop(gl.gl_queue_DF_Data.index, inplace=True)
        gl.gl_queue_DF_Data = gl.gl_queue_DF_Data.loc[:, API_Config.cfg['activework_field']]  # 取值列保存到csv
        gl.gl_queue_DF_Data.to_csv(API_Config.cfg["activework_path"], sep='\t')
        # 清空workdatalog
        pdcsv.clearCSV();
        print("==================================================")
        print("======↓↓↓↓↓", datetime.datetime.now(), "↓↓↓↓↓======")
        print("==================================================")
        pass
    else:
        pass

    # 继续执行下次timer的定时器查询执行任务
    t = Timer(interval, auto_trade, (interval,))
    t.start()

# 定时器 定时调用
t_exec = Timer(2, auto_trade, (2,))
t_exec.start()







