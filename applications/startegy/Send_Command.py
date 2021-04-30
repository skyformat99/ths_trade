import requests
import json

se = requests.session()
def InputQueue(post_data):
    print("开始发送:", post_data)
    try:
        res_post = se.post("http://127.0.0.1:6003/api/queue", json=post_data)
    except Exception as Ex:
        raise Ex

    res = json.loads(res_post.text)

    if res["code"] != 200:
        print(res)
        raise Exception(res["msg"])
    else:
        print("成功处理")
