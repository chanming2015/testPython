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

from base import format_reality_nlu, format_reality_command, format_reality_command_inspire, textRequest

# 设置产品ID
PRODUCT_ID = "279606354"
# 设置分支
BRANCH = "car_ctl_beta_test"
# 设置授权APIKEY；DUI开放平台-授权管理
APIKEY = ""
# True：单轮测试；False：多轮测试
is_single_round_test = False

# 必填参数非空校验
if PRODUCT_ID == "" or BRANCH == "" or APIKEY == "":
    print("请设置产品ID、分支、授权APIKEY！")
    exit(1)

# 定义测试服务地址
SERVER_URL = "wss://dds.dui.ai/dds/v3/%s?serviceType=websocket&productId=%s&apikey=%s&deviceName=carCtlDmTestAutoTest&communicationType=fullDuplex" % (BRANCH, PRODUCT_ID, APIKEY)
# 读取Excel文件测试数据
file_name = "多轮车控测试集.xlsx"
excel_file = pd.ExcelFile(file_name)

# 执行webSocket请求，执行测试
async def do_test(lines_data):
    session_id = uuid4().hex
    print("start time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # 打印webSocket连接地址
    print("webSocket连接地址：%s" % SERVER_URL)
    # 创建webSocket连接
    async with websockets.connect(SERVER_URL, ping_interval=None, ping_timeout=None) as websocket:
        #         resp = await systemSetting(websocket)
        # 循环测试数据
        for datas in lines_data[1:]:
            # 获取测试用例
            refText = datas[index_refText]
            
            # 遇到空白行，表示一轮测试结束，下一轮测试开始（使用新的sessionId）
            if refText is None or refText == "" or type(refText) != str:
                session_id = uuid4().hex
                continue
            
            if is_single_round_test:
                # 单轮测试用例，每次更新sessionId
                session_id = uuid4().hex
            
            if type(datas[index_reality]) is str and datas[index_reality].strip().startswith("{"):
                resp = datas[index_reality]
            else:
                resp = await textRequest(websocket, refText, session_id)
            # 解析测试返回结果
            result = json.loads(resp)

            # 写入测试结果
            datas[index_reality] = resp
            if result.get("skill") is not None:
                datas[index_skill] = result["skill"]
            if result.get("dm") is not None:
                if result["dm"].get("task") is not None:
                    datas[index_task] = result["dm"]["task"]
                if result["dm"].get("intentName") is not None:
                    datas[index_intent] = result["dm"]["intentName"]
                if result.get("nlu") is not None and result["nlu"].get("semantics") is not None:
                    datas[index_nlu] = format_reality_nlu(result["nlu"])
                if result["dm"].get("command") is not None:
                    datas[index_command] = format_reality_command(result["dm"]["command"])
                elif result["dm"].get("inspire") is not None:
                    datas[index_command] = format_reality_command_inspire(result["dm"]["inspire"])
                if result["dm"].get("nlg") is not None:
                    datas[index_nlg] = result["dm"]["nlg"]

with pd.ExcelWriter("测试结果-" + file_name) as writer:
    # 遍历所有工作表
    for sheet_name in excel_file.sheet_names:
        lines = pd.read_excel(file_name, sheet_name=sheet_name, header=None).values.tolist()
        file_head = lines[0]
        
        # 定义测试数据列索引
        index_refText = file_head.index("测试用例")
        index_skill = file_head.index("实际技能")
        index_task = file_head.index("实际任务")
        index_intent = file_head.index("实际意图")
        index_nlu = file_head.index("实际语义")
        index_command = file_head.index("实际command")
        index_nlg = file_head.index("实际nlg")
        index_reality = file_head.index("实际结果")
        
        try:
            asyncio.get_event_loop().run_until_complete(do_test(lines))
        except Exception as e:
            print(e)

        # 回写数据结果到Excel文件
        df = pd.DataFrame(lines[1:], columns=file_head)
        df.to_excel(writer, sheet_name=sheet_name, index=False, header=True)
    
print("end time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print("测试完成！")
