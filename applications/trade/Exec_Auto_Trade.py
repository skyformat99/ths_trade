
from applications.trade.server.THS_Trader_Server import THSTraderServer
from applications.tool.CSV_Helper import CSVHelper
from applications.work_queue.ActiveWork import ActiveWork
import uuid
from pandas.io.json import json_normalize
import  applications.API_Config as API_Config

# 自动化交易初始化
ths = THSTraderServer()
# 活动的工作流初始化
aw = ActiveWork()
pdcsv = CSVHelper()

def to_df(item,entrust_no):
    data = {}
    data["key"] = str(uuid.uuid1())
    # key   委托时间	证券代码	证券名称	操作	备注	委托数量	成交数量	委托价格	成交均价	撤消数量	合同编号	策略编号
    data["委托时间"] = ""
    data["证券代码"] = str(item['stock_no'])
    data["证券名称"] = str(item['stock_name'])
    data["操作"] = ''
    data["备注"] = ''
    data["委托数量"] = item['amount']
    data["成交数量"] = -1
    data["委托价格"] = -1
    data["成交均价"] = -1
    data["撤消数量"] = -1
    data["合同编号"] = entrust_no
    data["策略编号"] = str(item["strategy_no"])
    df = json_normalize(data)  # json转换dataframe
    df.head()
    return df


def exec_run(item):

    if item['operate'] == 'buy':
        print('========得到买入指令', item['stock_no'], item['amount'])
        result = ths.buy(item)
        if result["auto"]:  # True:自动化程序返回   False:接口程序返回
            if result['success']:
                print("合同号:", result['entrust_no'])
                # grid = ths.get_today_entrusts()
                # print("grid:", grid)
                # grid = grid.astype({'合同编号': 'str'})
                # print(" str(result['entrust_no']):",  str(result['entrust_no']))
                # df_where = grid[grid['合同编号'] == str(result['entrust_no'])]  # 查找符合条件的合同号的数据条目
                # print("df_where", df_where)
                # df_where["key"] = str(uuid.uuid1())  # 增加唯一标识
                # df_where["策略编号"] = str(item["strategy_no"])
                # df = pdcsv.getCVS()  # 读取现有的csv
                # df = pdcsv.addCSV(df, df_where)  # 组合现有的csv
                # pdcsv.saveCSV(df)  # 写入新的dataframe 到csv

                # 以上的这种方式时每次执行完一支股票后 紧接着去查询委托数据(弊端交易10次 就要获取10次 费时间)
                # 尝试按照把所有的活干完之后再统一去查委托进行填充数据的方式替代(省时间)
                df_1 = to_df(item, str(result['entrust_no']))
                df = pdcsv.getCVS()  # 读取现有的csv
                df = pdcsv.addCSV(df, df_1)  # 组合现有的csv
                pdcsv.saveCSV(df)  # 写入新的dataframe 到csv
            else:
                print(result['msg'])
        else:
            # 接口程序拦截到金额不足返回
            result["result"]["key"] = str(uuid.uuid1())  # 增加唯一标识
            result["result"]["策略编号"] = str(item["strategy_no"])
            df1 = json_normalize(result['result'])
            df = pdcsv.getCVS()  # 读取现有的csv
            df = pdcsv.addCSV(df, df1)  # 组合现有的csv
            pdcsv.saveCSV(df)  # 写入新的dataframe 到csv

    if item['operate'] == 'sell':
        print('========得到卖出指令', item['stock_no'], item['amount']);
        result = ths.sell(item)
        if result["auto"]:  # True:自动化程序返回   False:接口程序返回
            if result['success']:
                print("合同号:", result['entrust_no'])
                # grid = ths.get_today_entrusts()  # 获取市价委托F8 中的grid
                # print("grid:",grid)
                # grid = grid.astype({'合同编号': 'str'})
                # df_where = grid[grid['合同编号'] == str(result['entrust_no'])]  # 查找符合条件的合同号的数据条目
                # df_where["key"] = str(uuid.uuid1())  # 增加唯一标识
                # df_where["策略编号"] = item["strategy_no"]
                # df = pdcsv.getCVS()  # 读取现有的csv
                # df = pdcsv.addCSV(df, df_where)  # 组合现有的csv
                # pdcsv.saveCSV(df)  # 写入新的dataframe 到csv

                # 以上的这种方式时每次执行完一支股票后 紧接着去查询委托数据(弊端交易10次 就要获取10次 费时间)
                # 尝试按照把所有的活干完之后再统一去查委托进行填充数据的方式替代(省时间)
                df_1 = to_df(item, str(result['entrust_no']))
                df = pdcsv.getCVS()  # 读取现有的csv
                df = pdcsv.addCSV(df, df_1)  # 组合现有的csv
                pdcsv.saveCSV(df)  # 写入新的dataframe 到csv

            else:
                print(result['msg'])
        else:
            # 接口程序拦截到股份不足返回
            result["result"]["key"] = str(uuid.uuid1())  # 增加唯一标识
            result["result"]["策略编号"] = str(item["strategy_no"])
            df1 = json_normalize(result['result'])
            df = pdcsv.getCVS()  # 读取现有的csv
            df = pdcsv.addCSV(df, df1)  # 组合现有的csv
            pdcsv.saveCSV(df)  # 写入新的dataframe 到csv

    if (item['operate'] == 'get_position'):
        return ths.get_position()

    if (item['operate'] == 'get_today_trades'):
        return ths.get_today_trades()

    if (item['operate'] == 'get_today_entrusts'):
        return ths.get_today_entrusts()

    if (item['operate'] == 'get_balance'):
        return ths.get_balance()

    # 做完一个 更新状态
    aw.edit_queue_the_one_status(item['key'])
