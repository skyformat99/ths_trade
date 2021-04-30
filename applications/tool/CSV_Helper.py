import pandas as pd
from applications import API_Config


class CSVHelper:
    def __init__(self):
        pass

    def getCVS(self, path=API_Config.cfg['workdatalog_path']):
        """ 获取csv数据 """
        df = pd.read_csv(path, sep='\t')
        df = df.loc[:, API_Config.cfg['workdata_field']]
        return df

    def addCSV(self, df, item):
        """ 添加csv数据  item:要添加的行数据   df:向df中添加"""
        item = item.loc[:, API_Config.cfg['workdata_field']]
        df = pd.concat([df, item])
        df = df.loc[:, API_Config.cfg['workdata_field']]
        df = df.reset_index(drop=True)
        return df

    def editCSV(self, df, entrust_no, strategy_no, value):
        """ 修改csv数据   entrust_no:合同编号  strategy_no:策略编号   """
        if (entrust_no == "" | strategy_no == ""):
            print('合同编号或策略编号有空值!')
            return False;
        df.loc[df['合同编号'] == entrust_no & df['策略编号'] == strategy_no, '合同编号'] = value
        return df;

    def saveCSV(self, df, path=API_Config.cfg['workdatalog_path']):
        """ 保存csv """
        df = df.loc[:, API_Config.cfg['workdata_field']]
        df = df.astype({'策略编号': 'str'})
        df.to_csv(path, sep='\t')

    def clearCSV(self, path=API_Config.cfg['workdatalog_path']):
        df= self.getCVS()
        df.drop(df.index, inplace=True)
        df = df.loc[:, API_Config.cfg['workdata_field']]  # 取值列保存到csv
        df.to_csv(path, sep='\t')
