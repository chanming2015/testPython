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
file_name = "车控测试集.xlsx"
sheet_name = "车控测试集"
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


# 解析实际语义函数
def parse_reality_nlu(nlu):
    reality_nlu_map = {}
    for slot in nlu["semantics"]["request"]["slots"]:
        reality_nlu_map[slot["name"]] = slot["value"]
        if slot.get("rawvalue") is not None:
            reality_nlu_map[slot["name"] + "_raw"] = slot["rawvalue"]
    return reality_nlu_map


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

            datas[index_reality] = resp
            # 比较技能、任务、意图、语义、command、nlg
            if type(datas[index_skill]) == str and datas[index_skill].strip() != "" and datas[index_skill] != result["skill"]:
                datas[index_error_message] = "技能错误，实际返回结果：%s" % result["skill"]
                continue
            if type(datas[index_task]) == str and datas[index_task].strip() != "" and datas[index_task] != result["dm"]["task"]:
                datas[index_error_message] = "任务错误，实际返回结果：%s" % result["dm"]["task"]
                continue
            if type(datas[index_intent]) == str and datas[index_intent].strip() != "" and datas[index_intent] != result["dm"]["intentName"]:
                datas[index_error_message] = "意图错误，实际返回结果：%s" % result["dm"]["intentName"]
                continue
            if type(datas[index_nlu]) == str and datas[index_nlu].strip() != "":
                if result.get("nlu") is None:
                    datas[index_error_message] = "语义错误，实际返回结果：无"
                    continue
                reality_nlu = parse_reality_nlu(result["nlu"])
                for kv_str in datas[index_nlu].strip().split("\n"):
                    kvs = kv_str.split("=")
                    if kvs[1] != reality_nlu.get(kvs[0]):
                        datas[index_error_message] = "语义错误，无法匹配：%s，实际返回结果：%s" % (kv_str, json.dumps(reality_nlu, ensure_ascii=False))
                        break
            if type(datas[index_command]) == str and datas[index_command].strip() != "":
                if result["dm"].get("command") is None:
                    datas[index_error_message] = "command错误，实际返回结果：无"
                    continue
                reality_command = result["dm"]["command"]
                for kv_str in datas[index_command].strip().split("\n"):
                    kvs = kv_str.split("=")
                    reality_command_value = None
                    if kvs[0].find(".") > 0:
                        for k in kvs[0].split("."):
                            if reality_command_value is None:
                                reality_command_value = reality_command.get(k, {})
                            else:
                                reality_command_value = reality_command_value.get(k)
                    else:
                        reality_command_value = reality_command.get(kvs[0])
                    if kvs[1] != reality_command_value:
                        datas[index_error_message] = "command错误，无法匹配：%s，实际返回结果：%s" % (kv_str, json.dumps(reality_command, ensure_ascii=False))
                        break
            if type(datas[index_nlg]) == str and datas[index_nlg].strip() != "":
                if result["dm"].get("nlg") is None or result["dm"]["nlg"] == "":
                    datas[index_error_message] = "nlg错误，实际返回结果：无"
                    continue
            else:
                if result["dm"].get("nlg") is not None and result["dm"]["nlg"] != "":
                    datas[index_error_message] = "nlg错误，实际返回结果：%s" % result["dm"]["nlg"]
                    continue


asyncio.get_event_loop().run_until_complete(do_test())

# 回写数据结果到Excel文件
df = pd.DataFrame(lines[1:], columns=file_head)
df.to_excel("测试结果-" + file_name, sheet_name="%s-%s-%s" % (sheet_name, PRODUCT_ID, BRANCH), index=False, header=True)
print("测试完成！")
