#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2023-03-25

@author: XuMaosen
"""
import asyncio
import json
import time
from uuid import uuid4

import pandas as pd
import websockets

# 设置产品ID
PRODUCT_ID = "279606354"
# 设置分支
BRANCH = "car_ctl_beta_test"
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
sheet_name = "单轮车控测试集"
lines = pd.read_excel(file_name, sheet_name=sheet_name, header=None).values.tolist()
file_head = lines[0]

# 定义测试数据列索引
index_refText = file_head.index("测试用例")
# 期望值数据列
index_skill = file_head.index("技能")
index_task = file_head.index("任务")
index_intent = file_head.index("意图")
index_nlu = file_head.index("语义")
index_command = file_head.index("command")
index_nlg = file_head.index("nlg")
# 比较错误提示
index_error_message = file_head.index("错误提示")
# 实际值数据列
index_reality_skill = file_head.index("实际技能")
index_reality_task = file_head.index("实际任务")
index_reality_intent = file_head.index("实际意图")
index_reality_nlu = file_head.index("实际语义")
index_reality_command = file_head.index("实际command")
index_reality_nlg = file_head.index("实际nlg")
index_reality_result = file_head.index("实际结果")

str_split_line = "--------------------"

# 解析实际语义函数
def parse_reality_nlu(nlu):
    reality_nlu_map = {}
    if nlu.get("semantics") is not None:
        for slot in nlu["semantics"]["request"]["slots"]:
            reality_nlu_map[slot["name"]] = slot["value"]
            if slot.get("rawvalue") is not None:
                reality_nlu_map[slot["name"] + "_raw"] = slot["rawvalue"]
    return reality_nlu_map


# 格式化实际语义，换行显示
def format_reality_nlu(nlu):
    reality_nlu = []
    if nlu.get("semantics") is not None:
        for slot in nlu["semantics"]["request"]["slots"]:
            if "intent" == slot["name"]:
                reality_nlu.append(str_split_line)
            else:
                reality_nlu.append(slot["name"] + "=" + slot["value"])
                if slot.get("rawvalue") is not None:
                    reality_nlu.append(slot["name"] + "_raw=" + slot["rawvalue"])
        if len(reality_nlu) > 0 and str_split_line == reality_nlu[0]:
            reality_nlu = reality_nlu[1:]
    return "\n".join(reality_nlu)


# 格式化实际command，换行显示
def format_reality_command(command):
    reality_command = ["api=" + command["api"]]
    if command.get("param") is not None:
        for k, v in command["param"].items():
            reality_command.append("param." + k + "=" + v)
    return "\n".join(reality_command)


# 格式化实际inspire command，换行显示
def format_reality_command_inspire(inspire):
    reality_command = []
    for ins in inspire:
        if ins.get('command') is not None:
            reality_command.append(str_split_line)
            reality_command.append(format_reality_command(ins['command']))
    if len(reality_command) > 0 and str_split_line == reality_command[0]:
        reality_command = reality_command[1:]
    return "\n".join(reality_command)


async def textRequest(ws, refText, sessionId=None):
    time.sleep(0.2)
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
    print("start time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # 打印webSocket连接地址
    print("webSocket连接地址：%s" % SERVER_URL)
    # 创建webSocket连接
    async with websockets.connect(SERVER_URL, ping_interval=None, ping_timeout=None) as websocket:
        # 循环测试数据
        for datas in lines[1:]:
            # 获取测试用例
            refText = datas[index_refText]
            
            # 遇到空白行，表示一轮测试结束，下一轮测试开始（使用新的sessionId）
            if refText is None or refText == "" or type(refText) != str:
                session_id = uuid4().hex
                continue
            
            if is_single_round_test:
                # 单轮测试用例，每次更新sessionId
                session_id = uuid4().hex
            
            if type(datas[index_reality_result]) is str and datas[index_reality_result].strip().startswith("{"):
                resp = datas[index_reality_result]
            else:
                resp = await textRequest(websocket, refText, session_id)
            # 解析测试返回结果
            datas[index_reality_result] = resp
            try:
                result = json.loads(resp)
            except Exception:
                datas[index_error_message] = "返回结果不是json格式"
                continue

            if result.get("skill") is not None:
                datas[index_reality_skill] = result.get("skill")
            if result["dm"].get("task") is not None:
                datas[index_reality_task] = result["dm"].get("task")
            if result["dm"].get("intentName") is not None:
                datas[index_reality_intent] = result["dm"].get("intentName")
            if result.get("nlu", {}).get('semantics') is not None:
                datas[index_reality_nlu] = format_reality_nlu(result["nlu"])
            if result["dm"].get("command") is not None:
                reality_command_str = format_reality_command(result["dm"]["command"])
                datas[index_reality_command] = reality_command_str
                if reality_command_str.find("param.vague_type_cmd=1") > 0:
                    datas[index_nlg] = "模糊指令的NLG"
            elif result["dm"].get("inspire") is not None:
                reality_command_str = format_reality_command_inspire(result["dm"]["inspire"])
                datas[index_reality_command] = reality_command_str
                if reality_command_str.find("param.vague_type_cmd=1") > 0:
                    datas[index_nlg] = "模糊指令的NLG"
            if result["dm"].get("nlg") is not None and result["dm"]["nlg"] != "":
                datas[index_reality_nlg] = result["dm"]["nlg"]

            # 比较技能
            if type(datas[index_skill]) is str and datas[index_skill].strip() != "":
                if datas[index_skill] != result.get("skill"):
                    datas[index_error_message] = "技能错误，预期返回结果：%s，实际返回结果：%s" % (datas[index_skill], result.get("skill"))
                    continue
            else:
                if result.get("skill") is not None:
                    datas[index_error_message] = "技能错误，预期返回结果：无，实际返回结果：%s" % result.get("skill")
                    continue

            # 比较任务
            if type(datas[index_task]) is str and datas[index_task].strip() != "":
                if datas[index_task] != result["dm"].get("task"):
                    datas[index_error_message] = "任务错误，预期返回结果：%s，实际返回结果：%s" % (datas[index_task], result["dm"].get("task"))
                    continue
            else:
                if result["dm"].get("task") is not None:
                    datas[index_error_message] = "任务错误，预期返回结果：无，实际返回结果：%s" % result["dm"].get("task")
                    continue

            # 比较意图
            if type(datas[index_intent]) is str and datas[index_intent].strip() != "":
                if datas[index_intent] != result["dm"].get("intentName"):
                    datas[index_error_message] = "意图错误，预期返回结果：%s，实际返回结果：%s" % (datas[index_intent], result["dm"].get("intentName"))
                    continue
            # else:
            #     if result["dm"].get("intentName") is not None:
            #         datas[index_error_message] = "意图错误，预期返回结果：无，实际返回结果：%s" % result["dm"].get("intentName")
            #         continue

            # 比较语义
            if type(datas[index_nlu]) is str and datas[index_nlu].strip() != "":
                if result.get("nlu", {}).get('semantics') is None:
                    datas[index_error_message] = "语义错误，预期返回结果：有，实际返回结果：无"
                    continue
                reality_nlu = parse_reality_nlu(result["nlu"])
                for kv_str in datas[index_nlu].strip().split("\n"):
                    kvs = kv_str.split("=")
                    if kvs[1] != reality_nlu.get(kvs[0]):
                        datas[index_error_message] = "语义错误，预期返回结果：%s，实际返回结果：%s" % (kv_str, "%s=%s" % (kvs[0], reality_nlu.get(kvs[0])))
                        break
#             else:
#                 if result.get("nlu", {}).get('semantics') is not None:
#                     datas[index_error_message] = "语义错误，预期返回结果：无，实际返回结果：有"
#                     continue

            # 比较command
            if type(datas[index_command]) is str and datas[index_command].strip() != "":
                if result["dm"].get("command") is None:
                    datas[index_error_message] = "command错误，预期返回结果：有，实际返回结果：无"
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
                        datas[index_error_message] = "command错误，预期返回结果：%s，实际返回结果：%s" % (kv_str, "%s=%s" % (kvs[0], reality_command_value))
                        break
            else:
                if result["dm"].get("command") is not None:
                    datas[index_error_message] = "command错误，预期返回结果：无，实际返回结果：有"
                    continue

            # 比较nlg
            if type(datas[index_nlg]) is str and datas[index_nlg].strip() != "":
                if result["dm"].get("nlg") is None or result["dm"]["nlg"] == "":
                    datas[index_error_message] = "nlg错误，预期返回结果：有，实际返回结果：无"
                    continue
            else:
                if result["dm"].get("nlg") is not None and result["dm"]["nlg"] != "":
                    datas[index_error_message] = "nlg错误，预期返回结果：无，实际返回结果：有"
                    continue

try:
    asyncio.get_event_loop().run_until_complete(do_test())
except Exception as e:
    print(e)

# 回写数据结果到Excel文件
df = pd.DataFrame(lines[1:], columns=file_head)
df.to_excel("测试结果-" + file_name, sheet_name="%s-%s" % (PRODUCT_ID, BRANCH), index=False, header=True)
print("end time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print("测试完成！")
