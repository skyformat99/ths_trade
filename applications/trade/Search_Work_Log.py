from applications.tool.CSV_Helper import CSVHelper
import applications.trade.Exec_Auto_Trade as ExecAutoTrade

pdcsv = CSVHelper()

def searchWorkLog(item):
    # 读取工作数据记录
    dfwork= pdcsv.getCVS()
    # 筛选符合此条件的策略数据
    dfwork = dfwork.astype({'策略编号': 'str'})
    dfwork = dfwork[dfwork['策略编号'] == str(item['strategy_no'])]
    # 再次查找市价委托得到数据集
    dfgrid = ExecAutoTrade.exec_run(item)

    # 循环判断获取符合此策略的所有合同号

    # 对于每一行，通过列名name访问对应的元素
    for workrow in dfwork.iterrows():
        if str(workrow[1]['合同编号']) == "0":
            pass
        else:
            # 对合同号不为0 的进行查验新的状态
            for gridrow in dfgrid.iterrows():
                if str(workrow[1]['合同编号']) == str(gridrow[1]['合同编号']):
                    # 更新成交状态
                    dfwork.loc[dfwork['合同编号'] == workrow[1]['合同编号'], '备注'] = str(gridrow[1]['备注'])
                    pass
            pass
    # 返回结果集
    return dfwork
