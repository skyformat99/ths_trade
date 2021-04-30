from common.CommonHandler import CommonHandler
from trest.router import post
import json
from applications.work_queue.ActiveWork import ActiveWork
import applications.api.business.Queue_Business as qb

aw = ActiveWork()

class autoHandler(CommonHandler):

    @post('queue')
    def queue(self):
        """ 初始化现有的csv文件 """

        # 获取调用接口的传参
        request_str = self.request.body   # self.request.body   self.request.arguments    self._postdata.keys()
        data_list = json.loads(request_str)  # 字符串转json
        if isinstance(data_list, str):
            data_list = json.loads(data_list)

        qb.InputQueue(request_str)
        res_json = data_list[0]["strategy_no"]
        return self.isOk(res_json)


class searchHandler(CommonHandler):
    @post('search')
    def searchresult(self):
        """ 查询结果 """
        request_str = self.request.body  # self.request.body   self.request.arguments    self._postdata.keys()
        resJSON = qb.SearchData(request_str)
        return self.isOk(resJSON)




