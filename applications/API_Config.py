cfg = {
    # 同花顺xiadan.exe 所在位置
    'exe_path': 'C:\\同花顺软件\\同花顺\\xiadan.exe',

    # 活动的工作流文件路径
    "activework_path": "./applications/work_queue/ActiveWork.csv",
    # 活动的工作流文件字段
    "activework_field": ["key", "strategy_no", "stock_no", "stock_name",
                         "amount", "operate", "status"],

    # 自动化交易工作数据记录文件路径
    "workdatalog_path": "./applications/Work_Data_Log.csv",
    # 保存csv的自动化交易工作记录
    'workdata_field': ["key", "委托时间", "证券代码", "证券名称", "操作", "备注",
                       "委托数量", "成交数量", "委托价格", "成交均价",
                       "撤消数量", "合同编号", "策略编号"],

    # 自动化交易休眠时间间隔
    "sleepA": 0.2,
    "sleepB": 0.5,
    "sleepC": 1,
}


