import hmac
import hashlib
import base64
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from urllib.parse import urlencode
import json
import websocket
import queue

def get_spark_response_yield(question, uid, spark_api_key, spark_api_secret, patch_id, app_id, service_id, temperature=0.5):
    """
    以流式方式获取讯飞星火大模型的回复内容。

    :param question: 用户的问题
    :param uid: 用户 ID
    :param spark_api_key: 讯飞星火的 API Key
    :param spark_api_secret: 讯飞星火的 API Secret
    :param patch_id: 资源 ID
    :param app_id: 应用的 App ID
    :param service_id: 服务 ID
    :param temperature: 温度参数，控制回复的随机性，默认为 0.5
    :yield: 流式返回的 content 内容
    """
    # 生成 date 参数
    cur_time = datetime.now()
    date = format_date_time(mktime(cur_time.timetuple()))

    # 生成 tmp 字符串
    host = "maas-api.cn-huabei-1.xf-yun.com"  # 确保与 WebSocket 地址一致
    path = "/v1.1/chat"
    tmp = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"

    # 生成签名
    tmp_sha = hmac.new(spark_api_secret.encode('utf-8'), tmp.encode('utf-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(tmp_sha).decode(encoding='utf-8')

    # 生成 authorization_origin
    authorization_origin = f"api_key='{spark_api_key}', algorithm='hmac-sha256', headers='host date request-line', signature='{signature}'"
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

    # 生成最终的 URL
    v = {
        "authorization": authorization,
        "date": date,
        "host": host
    }
    url = f"wss://{host}{path}?" + urlencode(v)

    # 创建一个队列，用于存储流式返回的内容
    content_queue = queue.Queue()

    # WebSocket 回调函数
    def on_message(ws, message):
        response = json.loads(message)
        if "payload" in response and "choices" in response["payload"]:
            for text in response["payload"]["choices"]["text"]:
                if text["content"]:  # 只返回非空内容
                    content_queue.put(text["content"])  # 将内容放入队列

        # 如果 status 为 2，表示回复结束
        if response["header"]["status"] == 2:
            content_queue.put(None)  # 放入结束标志

    def on_error(ws, error):
        print("Error:", error)
        content_queue.put(None)  # 放入结束标志

    def on_close(ws, close_status_code, close_msg):
        print("Connection closed")
        content_queue.put(None)  # 放入结束标志

    def on_open(ws):
        # 发送请求数据
        request_data = {
            "header": {
                "app_id": app_id,  # 替换为你的 app_id
                "uid": uid,  # 替换为你的 uid
                "patch_id": patch_id  # 替换为你的 patch_id
            },
            "parameter": {
                "chat": {
                    "domain": service_id,  # 替换为你的 service_id
                    "temperature": temperature
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {"role": "user", "content": question}  # 用户的问题
                    ]
                }
            }
        }
        ws.send(json.dumps(request_data))

    # 创建 WebSocket 连接
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open

    # 启动 WebSocket 连接（在单独的线程中运行）
    import threading
    threading.Thread(target=ws.run_forever).start()

    # 从队列中获取内容并 yield
    while True:
        content = content_queue.get()
        if content is None:  # 遇到结束标志，退出循环
            break
        yield content

# 示例调用
if __name__ == "__main__":
    # 替换为你的实际参数
    question = "请分析缩泉丸的组成成分（乌药、益智仁、山药）的中药功效"
    uid = "11"
    spark_api_key = "e0bd7dec00208de2d5ba8fda73c77c0e"
    spark_api_secret = "12ec2f5928298fe29a80cb2a4e97b98c"
    patch_id = ["1876273344855044096"]  # 确保是列表
    app_id = "59fd753c"
    service_id = "xqwen257bchat"

    # 调用函数并打印流式回复
    for content in get_spark_response_yield(question, uid, spark_api_key, spark_api_secret, patch_id, app_id, service_id):
        print(content, end="", flush=True)