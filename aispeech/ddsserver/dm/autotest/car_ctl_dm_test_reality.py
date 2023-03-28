#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2023-03-25

@author: XuMaosen
"""
import asyncio
import json
from uuid import uuid4

import pandas as pd
import websockets

# 设置产品ID
PRODUCT_ID = "279606354"
# 设置分支
BRANCH = "prod_p11"
# 设置授权APIKEY；DUI开放平台-授权管理
APIKEY = ""
# True：单轮测试；False：多轮测试
is_single_round_test = True

# 必填参数非空校验
if PRODUCT_ID == "" or BRANCH == "" or APIKEY == "":
    print("请设置产品ID、分支、授权APIKEY！")
    exit(1)

# 定义测试服务地址
SERVER_URL = "wss://dds.dui.ai/dds/v3/%s?serviceType=websocket&productId=%s&apikey=%s&deviceName=carCtlDmTestAutoTest&communicationType=fullDuplex" % (BRANCH, PRODUCT_ID, APIKEY)
# 读取Excel文件测试数据
file_name = "车控测试集2.xlsx"
sheet_name = "单轮车控测试集"
lines = pd.read_excel(file_name, sheet_name=sheet_name, header=None).values.tolist()
file_head = lines[0]

# 定义测试数据列索引
index_refText = file_head.index("测试用例")
index_skill = file_head.index("技能")
index_task = file_head.index("任务")
index_intent = file_head.index("意图")
index_nlu = file_head.index("语义")
index_command = file_head.index("command")
index_nlg = file_head.index("nlg")
index_error_message = file_head.index("错误提示")
index_reality = file_head.index("实际结果")


# 格式化实际语义，换行显示
def format_reality_nlu(nlu):
    reality_nlu = []
    for slot in nlu["semantics"]["request"]["slots"]:
        if "intent" != slot["name"]:
            reality_nlu.append(slot["name"] + "=" + slot["value"])
            if slot.get("rawvalue") is not None:
                reality_nlu.append(slot["name"] + "_raw=" + slot["rawvalue"])
    return "\n".join(reality_nlu)


# 格式化实际command，换行显示
def format_reality_command(command):
    reality_command = ["api=" + command["api"]]
    if command.get("param") is not None:
        for k, v in command["param"].items():
            reality_command.append("param." + k + "=" + v)
    return "\n".join(reality_command)


async def textRequest(ws, refText, sessionId=None):
    # 构造请求参数
    content = {
        "topic": 'nlu.input.text',
        "recordId": uuid4().hex,
        "refText": refText
    }
    if sessionId is not None:
        content["sessionId"] = sessionId
    try:
        # 发送请求
        print("请求参数：%s" % json.dumps(content, ensure_ascii=False))
        await ws.send(json.dumps(content))
        # 接收响应
        resp = await ws.recv()
        # print("响应结果：%s" % resp)
        return resp
    except websockets.WebSocketException as exp:
        print(exp)


# 执行webSocket请求，执行测试
async def do_test():
    session_id = uuid4().hex
    # 打印webSocket连接地址
    print("webSocket连接地址：%s" % SERVER_URL)
    # 创建webSocket连接
    async with websockets.connect(SERVER_URL) as websocket:
        # 循环测试数据
        for datas in lines[1:]:
            # 获取测试用例
            refText = datas[index_refText]
            # print("测试用例：%s" % refText)
            if is_single_round_test:
                # 单轮测试用例，每次更新sessionId
                session_id = uuid4().hex
            else:
                # 多轮测试用例，遇到空白行，表示一轮测试结束，下一轮测试开始（使用新的sessionId）
                if refText is None or refText == "" or type(refText) != str:
                    session_id = uuid4().hex
                    continue
            resp = await textRequest(websocket, refText, session_id)
            # 解析测试返回结果
            result = json.loads(resp)

            # 写入测试结果
            datas[index_reality] = resp
            if result.get("skill") is not None:
                datas[index_skill] = result["skill"]
            if result["dm"].get("task") is not None:
                datas[index_task] = result["dm"]["task"]
            if result["dm"].get("intentName") is not None:
                datas[index_intent] = result["dm"]["intentName"]
            if result.get("nlu") is not None and result["nlu"].get("semantics") is not None:
                datas[index_nlu] = format_reality_nlu(result["nlu"])
            if result["dm"].get("command") is not None:
                datas[index_command] = format_reality_command(result["dm"]["command"])
            if result["dm"].get("nlg") is not None:
                datas[index_nlg] = result["dm"]["nlg"]


asyncio.get_event_loop().run_until_complete(do_test())

# 回写数据结果到Excel文件
df = pd.DataFrame(lines[1:], columns=file_head)
df.to_excel("测试结果-" + file_name, sheet_name="%s-%s-%s" % (sheet_name, PRODUCT_ID, BRANCH), index=False, header=True)
print("测试完成！")
