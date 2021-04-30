import pywinauto
from pywinauto import clipboard, keyboard
import pandas as pd
import io
import time
import datetime
import sys

sys.path.append(r'../../tool')
from applications import API_Config


class THSTraderServer:

    def __init__(self, exe_path=API_Config.cfg['exe_path']):  # r"C:\同花顺软件\同花顺\xiadan.exe"
        # print(api_config.cfg['exe_path'])
        print("正在连接客户端:", exe_path, "...")
        self.app = pywinauto.Application().connect(path=exe_path, timeout=10)
        print("已连接到" + exe_path + ";")
        self.main_wnd = self.app.window(title="网上股票交易系统5.0")  # self.app.top_window()
        self.app.top_window().set_focus()
        self.__esc()

    def buy(self, item):
        """ 买入 """
        # self.app.top_window().set_focus();
        time.sleep(API_Config.cfg["sleepA"])
        try:
            self.__select_menu(['市价委托', '买入'])
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.__select_menu(['市价委托', '买入'])

        time.sleep(API_Config.cfg["sleepA"])

        try:
            self.app.top_window().window(control_id=0x3EF, class_name='Button').click()  # 重填按钮
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.app.top_window().window(control_id=0x3EF, class_name='Button').click()  # 重填按钮

        time.sleep(API_Config.cfg["sleepA"])

        try:
            # 设置股票代码
            self.main_wnd.window(control_id=0x408, class_name="Edit").type_keys(str(item['stock_no']))
        except:
            time.sleep(API_Config.cfg["sleepC"])
            # 设置股票代码
            self.main_wnd.window(control_id=0x408, class_name="Edit").type_keys(str(item['stock_no']))

        # 判断是否存在市场的二义性
        try:
            time.sleep(API_Config.cfg["sleepA"])
            top_text_title = ""
            try:
                print("try")
                top_text_title = self.app.top_window().window_text()
                print(top_text_title)
            except:
                print("except")
                time.sleep(API_Config.cfg["sleepC"])
                top_text_title = self.app.top_window().window_text()
                print(top_text_title)
            print("top_text_title:",top_text_title)
            if top_text_title == '':
                leftbutton = ""
                try:
                    leftbutton = self.app.top_window().window(control_id=0x7CD, class_name='Button')
                    lefttext = leftbutton.texts()
                except:
                    time.sleep(API_Config.cfg["sleepC"])
                    leftbutton = self.app.top_window().window(control_id=0x7CD, class_name='Button')
                    lefttext = leftbutton.texts()

                time.sleep(API_Config.cfg["sleepA"])
                rightbutton = ""
                try:
                    rightbutton = self.app.top_window().window(control_id=0x7AF, class_name='Button')
                    rigthtext = rightbutton.texts()
                except:
                    time.sleep(API_Config.cfg["sleepC"])
                    rightbutton = self.app.top_window().window(control_id=0x7AF, class_name='Button')
                    rigthtext = rightbutton.texts()

                time.sleep(API_Config.cfg["sleepA"])

                if str(item['stock_name']) in str(lefttext[0].replace('\n', '')):
                    leftbutton.click()
                if str(item['stock_name']) in str(rigthtext[0].replace('\n', '')):
                    rightbutton.click()
        except:
            pass
        time.sleep(API_Config.cfg["sleepA"])

        try:
            self.main_wnd.window(control_id=0x40A, class_name="Edit").type_keys(str(item['amount']))  # 设置股数目
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.main_wnd.window(control_id=0x40A, class_name="Edit").type_keys(str(item['amount']))  # 设置股数目

        time.sleep(API_Config.cfg["sleepA"])
        text = ""
        try:
            text = self.main_wnd.window(control_id=0x3FA, class_name="Static")  # 可买数量
        except:
            time.sleep(API_Config.cfg["sleepC"])
            text = self.main_wnd.window(control_id=0x3FA, class_name="Static")  # 可买数量

        time.sleep(API_Config.cfg["sleepA"])
        can_buy = text.texts()  # window_text()
        print('买入操作: 可买(股):', can_buy[0], "指令要求:", item['amount'])

        # 判断如果指令要求的数量超过可买数量则返回创建的失败对象
        if (int(item['amount']) > int(can_buy[0])) | ((int(item['amount']) % 100) > 0):
            # key	委托时间	证券代码	证券名称	操作	备注	委托数量	成交数量	委托价格	成交均价
            # 撤消数量	合同编号	策略编号
            remark1 = "资金不足:资金可用数不足,现可买" + str(can_buy[0]) + ",指令要买" + str(item['amount'])
            remark2 = "不可拆买:委托数量必须是每手股(张)数的倍数,指令要买" + str(item['amount'])
            remark = ""
            if int(item['amount']) > int(can_buy[0]):
                remark = remark1

            if (int(item['amount']) % 100) > 0:
                remark = remark2
            self.__esc()
            return {
                "success": False,
                "auto": False,  # True:自动化程序返回   False:接口程序返回
                "msg": "自动化执行程序拦截到错误",  # 资金可用数不足,尚需xx
                "result": {
                    "委托时间": datetime.datetime.now().strftime("%H:%M:%S"),
                    "证券代码": str(item['stock_no']),
                    "证券名称": "",
                    "操作": "买入",  # 五档买入
                    "备注": remark,
                    "委托数量": str(item['amount']),
                    "成交数量": "0",
                    "委托价格": "0",
                    "成交均价": "0",
                    "撤消数量": "0",
                    "合同编号": "0",
                    "策略编号": "",
                }
            }
        result = self.__trade()
        self.__esc()
        return result

    def sell(self, item):
        """ 卖出 """
        # self.app.top_window().set_focus();
        time.sleep(API_Config.cfg["sleepA"])
        try:
            self.__select_menu(['市价委托', '卖出'])
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.__select_menu(['市价委托', '卖出'])

        time.sleep(API_Config.cfg["sleepA"])

        try:
            self.app.top_window().window(control_id=0x3EF, class_name='Button').click()  # 重填按钮
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.app.top_window().window(control_id=0x3EF, class_name='Button').click()  # 重填按钮

        time.sleep(API_Config.cfg["sleepA"])
        # 设置股票代码
        try:
            self.main_wnd.window(control_id=0x408, class_name="Edit").type_keys(str(item['stock_no']))
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.main_wnd.window(control_id=0x408, class_name="Edit").type_keys(str(item['stock_no']))

        # 判断是否存在市场的二义性
        try:
            time.sleep(API_Config.cfg["sleepA"])
            top_text_title = ""
            try:
                print("try")
                top_text_title = self.app.top_window().window_text()
                print(top_text_title)
            except:
                print("except")
                time.sleep(API_Config.cfg["sleepC"])
                top_text_title = self.app.top_window().window_text()
                print(top_text_title)

            if top_text_title == '':
                # 如果市场有二义性会弹出窗口 里面有两个按钮  左边按钮和右边按钮   文本中包含股票名称
                leftbutton = ""
                try:
                    leftbutton = self.app.top_window().window(control_id=0x7CD, class_name='Button')
                    lefttext = leftbutton.texts()
                except:
                    time.sleep(API_Config.cfg["sleepC"])
                    leftbutton = self.app.top_window().window(control_id=0x7CD, class_name='Button')
                    lefttext = leftbutton.texts()

                rightbutton = ""
                try:
                    rightbutton = self.app.top_window().window(control_id=0x7AF, class_name='Button')
                    rigthtext = rightbutton.texts()
                except:
                    time.sleep(API_Config.cfg["sleepC"])
                    rightbutton = self.app.top_window().window(control_id=0x7AF, class_name='Button')
                    rigthtext = rightbutton.texts()

                time.sleep(API_Config.cfg["sleepA"])

                if str(item['stock_name']) in lefttext[0]:
                    leftbutton.click()
                if str(item['stock_name']) in rigthtext[0]:
                    rightbutton.click()
        except:
            pass

        time.sleep(API_Config.cfg["sleepA"])
        # 设置股数目
        try:
            self.main_wnd.window(control_id=0x40A, class_name="Edit").type_keys(str(item['amount']))
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.main_wnd.window(control_id=0x40A, class_name="Edit").type_keys(str(item['amount']))

        time.sleep(API_Config.cfg["sleepA"])
        text = ""
        try:
            text = self.main_wnd.window(control_id=0x40E, class_name="Static")
        except:
            time.sleep(API_Config.cfg["sleepC"])
            text = self.main_wnd.window(control_id=0x40E, class_name="Static")

        time.sleep(API_Config.cfg["sleepA"])
        can_sell = text.texts()  # window_text()
        print("卖出操作: 可用余额:", can_sell[0], "指令要求:", item['amount'])

        # 判断如果指令要求的数量超过可买数量则返回创建的失败对象
        if (int(item['amount']) > int(can_sell[0])) | ((int(item['amount']) % 100) > 0):
            # key	委托时间	证券代码	证券名称	操作	备注	委托数量	成交数量	委托价格	成交均价
            # 	撤消数量	合同编号	策略编号
            remark1 = "股份不足:股份可用数不足,现可用" + str(can_sell[0]) + "指令要卖" + str(item['amount'])
            remark2 = "不可拆卖:不允许将整股拆成零股来卖,指令要卖" + str(item['amount'])
            remark = "自动化执行程序拦截到错误"
            if int(item['amount']) > int(can_sell[0]):
                remark = remark1

            if (int(item['amount']) % 100) > 0:
                remark = remark2
            self.__esc()
            return {
                "success": False,
                "auto": False,  # True:自动化程序返回   False:接口程序返回
                "msg": "股份可用数不足",  # 股份可用数不足,尚需xx
                "result": {
                    "委托时间": datetime.datetime.now().strftime("%H:%M:%S"),
                    "证券代码": str(item['stock_no']),
                    "证券名称": "",
                    "操作": "卖出",  # 五档买入
                    "备注": remark,  # 股份可用数不足,尚需xx
                    "委托数量": str(item['amount']),
                    "成交数量": "0",
                    "委托价格": "0",
                    "成交均价": "0",
                    "撤消数量": "0",
                    "合同编号": "0",
                    "策略编号": "",
                }
            }
        result = self.__trade()
        self.__esc()
        return result

    def get_balance(self):
        """ 获取资金情况 """
        self.app.top_window().set_focus()
        time.sleep(API_Config.cfg["sleepA"])
        try:
            self.__select_menu(['查询[F4]', '资金明细'])
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.__select_menu(['查询[F4]', '资金明细'])

        time.sleep(API_Config.cfg["sleepB"])
        df = self.__get_grid_data()
        self.__esc()
        return df

    def get_position(self):
        """ 获取市价委托的F6持仓 """
        self.app.top_window().set_focus()
        time.sleep(API_Config.cfg["sleepA"])
        try:
            self.__select_menu(['市价委托', '卖出'])
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.__select_menu(['市价委托', '卖出'])

        time.sleep(API_Config.cfg["sleepB"])
        keyboard.send_keys('{VK_F6}')  # 点击持仓选项卡
        self.__click_update_button()
        time.sleep(API_Config.cfg["sleepA"])
        df = self.__get_grid_data()
        self.__esc()
        return df


    def get_today_trades(self):
        """ 获取市价委托的F7当日成交"""
        self.app.top_window().set_focus()
        time.sleep(API_Config.cfg["sleepA"])
        try:
            self.__select_menu(['市价委托', '卖出'])
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.__select_menu(['市价委托', '卖出'])

        time.sleep(API_Config.cfg["sleepB"])
        keyboard.send_keys('{VK_F7}')  # 点击成交选项卡
        self.__click_update_button()
        time.sleep(API_Config.cfg["sleepA"])
        df = self.__get_grid_data()
        self.__esc()
        return df

    def get_today_entrusts(self):
        """ 获取市价委托的F8委托 """
        self.app.top_window().set_focus()
        time.sleep(API_Config.cfg["sleepA"])
        try:
            self.__select_menu(['市价委托', '卖出'])
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.__select_menu(['市价委托', '卖出'])

        time.sleep(API_Config.cfg["sleepB"])
        keyboard.send_keys('{VK_F8}')  # 点击持仓选项卡
        self.__click_update_button()
        time.sleep(API_Config.cfg["sleepA"])
        df = self.__get_grid_data()
        self.__esc()
        return df

    def __trade(self):  # stock_no, amount
        """ 交易 """
        time.sleep(API_Config.cfg["sleepA"])
        # 设置最优五档即时成交剩余转撤销申报
        select = ""
        try:
            select = self.main_wnd.window(control_id=0x605, class_name="ComboBox")
        except:
            time.sleep(API_Config.cfg["sleepC"])
            select = self.main_wnd.window(control_id=0x605, class_name="ComboBox")

        time.sleep(API_Config.cfg["sleepA"])
        try:
            # 深A 索引4
            select.select(3)
        except:
            # 沪A 索引0
            select.select(0)

        time.sleep(API_Config.cfg["sleepA"])
        # 点击卖出or买入
        try:
            self.main_wnd.window(control_id=0x3EE, class_name="Button").click()
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.main_wnd.window(control_id=0x3EE, class_name="Button").click()

        # 系统设置 快速交易设置中 委托成功后弹出提示对话框  弹出对话框获取合同号
        time.sleep(API_Config.cfg["sleepB"])
        time.sleep(API_Config.cfg["sleepC"])  # 再等待1秒给交易预留
        # 获取弹窗文本
        try:
            print("结果try")
            result = self.app.top_window().window(control_id=0x3EC, class_name='Static')
            if result.exists():
                result = result.window_text()
            else:
                time.sleep(API_Config.cfg["sleepC"])
                result = self.app.top_window().window(control_id=0x3EC, class_name='Static')
                result = result.window_text()
        except:
            print("结果except")
            time.sleep(API_Config.cfg["sleepC"])
            result = self.app.top_window().window(control_id=0x3EC, class_name='Static')
            result = result.window_text()
            print("结果",result)


        try:
            print("弹窗确定try")
            self.app.top_window().set_focus()
            # 买入卖出成功  或  买入卖出错误的提示窗口中的确认按钮  确定0x2
            self.app.top_window().window(control_id=0x2, class_name='Button').click()  # 确定
        except:
            print("弹窗确定except")
            self.app.top_window().set_focus()
            time.sleep(API_Config.cfg["sleepC"])
            self.app.top_window().window(control_id=0x2, class_name='Button').click()  # 确定

        return self.__parse_result(result)

    def __get_grid_data(self, is_records=False):
        """ 获取grid里面的数据 """
        time.sleep(API_Config.cfg["sleepC"])  # 等待1秒是 因为等待加载到数据后再去获取grid
        try:
            self.main_wnd.window(control_id=0x417, class_name='CVirtualGridCtrl').set_focus()
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.main_wnd.window(control_id=0x417, class_name='CVirtualGridCtrl').set_focus()

        keyboard.send_keys('{VK_APPS}')  # 键盘鼠标右键
        time.sleep(API_Config.cfg["sleepA"])
        keyboard.send_keys('c')  # 发送c 软件中的复制功能通过右键实现(ctrl+c快捷键不起作用)
        time.sleep(API_Config.cfg["sleepA"])
        data = clipboard.GetData()  # 读取剪贴板数据
        df = pd.read_csv(io.StringIO(data), delimiter='\t', na_filter=False)
        if is_records:
            return df.to_dict('records')
        else:
            return df

    def __select_menu(self, path):
        """ 点击左边菜单 """
        if r"网上股票" not in self.app.top_window().window_text():
            self.app.top_window().set_focus()
            pywinauto.keyboard.send_keys("{ENTER}")
        self.__get_left_menus_handle().get_item(path).click()

    def __get_left_menus_handle(self):
        while True:
            try:
                handle = ""
                try:
                    handle = self.main_wnd.window(control_id=0x81, class_name='SysTreeView32')
                except:
                    time.sleep(API_Config.cfg["sleepC"])
                    handle = self.main_wnd.window(control_id=0x81, class_name='SysTreeView32')
                handle.wait('ready', 2)
                return handle
            except Exception as ex:
                print(ex)
                pass

    def __click_update_button(self):
        """ 刷新按钮 """
        print('刷新')
        time.sleep(API_Config.cfg["sleepA"])
        try:
            self.main_wnd.window(control_id=0x8016, class_name='Button').click()
        except:
            time.sleep(API_Config.cfg["sleepC"])
            self.main_wnd.window(control_id=0x8016, class_name='Button').click()

        time.sleep(API_Config.cfg["sleepB"])

    @staticmethod
    def __parse_result(result):
        """ 解析买入卖出的结果 """
        # "您的买入委托已成功提交，合同编号：865912566。"
        # "您的卖出委托已成功提交，合同编号：865967836。"
        # "您的撤单委托已成功提交，合同编号：865967836。"
        # "系统正在清算中，请稍后重试！ "
        if r"已成功提交，合同编号：" in result:
            return {
                "success": True,
                "auto": True,  # True:自动化程序返回   False:接口程序返回
                "msg": result,
                "entrust_no": result.split("合同编号：")[1].split("。")[0]
            }
        else:
            return {
                "success": False,
                "auto": True,  # True:自动化程序返回   False:接口程序返回
                "msg": result
            }

    def __esc(self):
        time.sleep(API_Config.cfg["sleepB"])
        try:
            # self.app.top_window().window(control_id=0x3F0, class_name='Button').click()  # 二义性的弹窗右上角的关闭按钮
            self.app.top_window().set_focus()
            pywinauto.keyboard.send_keys('{VK_ESCAPE}')
            time.sleep(API_Config.cfg["sleepA"])
            try:
                self.app.top_window().window(control_id=0x3EF, class_name='Button').click()  # 重填按钮
            except:
                time.sleep(API_Config.cfg["sleepC"])
                self.app.top_window().window(control_id=0x3EF, class_name='Button').click()  # 重填按钮

        except:
            pass
        self.app.top_window().set_focus()
        pywinauto.keyboard.send_keys('{VK_ESCAPE}')
        time.sleep(API_Config.cfg["sleepA"])
        self.__select_menu([0])
