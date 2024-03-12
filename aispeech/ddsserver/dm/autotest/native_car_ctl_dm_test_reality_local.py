#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2023-03-25

@author: XuMaosen
"""
import json
import time
from uuid import uuid4
from base import format_reality_command, format_reality_command_inspire

import pandas as pd
import requests

# 定义测试服务地址
SERVER_URL = "http://localhost:8080/v2/lyra/webhook/dsk/car/ctl"
# 读取Excel文件测试数据
pid = "279615509"
file_name = "车控native测试集-标定对比.xlsx"
sheet_name = pid + "-car_ctl_beta_test"
lines = pd.read_excel(file_name, sheet_name=sheet_name, header=None).values.tolist()
file_head = lines[0]

# True：单轮测试；False：多轮测试
is_single_round_test = True

# 定义测试数据列索引
index_refText = file_head.index("测试用例")
index_reality = file_head.index("实际结果")
index_reality_command = file_head.index("实际command")
index_reality_nlg = file_head.index("实际nlg")
index_local_command = file_head.index("本地command")
index_local_nlg = file_head.index("本地nlg")
index_local = file_head.index("本地结果")


def jsonRequest(requestData, sessionId=None):
    content = requestData
    resp = requests.post(SERVER_URL, json=content)
    return resp.text


def format_local_command(command):
    command_out = {}
    command_out["api"] = command["url"].replace("nativecmd://", "").replace("nativeapi://", "")
    command_out["param"] = command.get("args")
    return command_out


# 执行webSocket请求，执行测试
def do_test():
    session_id = uuid4().hex
    print("start time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # 打印webSocket连接地址
    print("http地址：%s" % SERVER_URL)
    
    # 循环测试数据
    for datas in lines[1:]:
        # 获取测试用例
        refText = datas[index_refText]
        if is_single_round_test:
            # 单轮测试用例，每次更新sessionId
            session_id = uuid4().hex
        else:
            # 多轮测试用例，遇到空白行，表示一轮测试结束，下一轮测试开始（使用新的sessionId）
            if refText is None or refText == "" or type(refText) != str:
                session_id = uuid4().hex
                continue
        
        if type(datas[index_local]) is str or type(datas[index_reality]) is not str:
            continue
        print("测试用例：%s" % refText)
        requestData = json.loads(refText)
        if requestData is not None:
            resp = jsonRequest(requestData, session_id)
            
            # 解析测试返回结果
            result = json.loads(resp)
            
            if result.get("dm") is None:
                result["dm"] = {}
            if result.get("response") is None and result.get("dm").get("response") is not None:
                result["response"] = result.get("dm").get("response")
            
            if result.get("response") is not None:
                if result["response"].get("execute") is not None:
                    result["dm"]["command"] = format_local_command(result["response"]["execute"])
                elif result["response"].get("inspire") is not None:
                    result["dm"]["inspire"] = result["response"].get("inspire")
                if result["response"].get("speak") is not None:
                    result["dm"]["nlg"] = result["response"]["speak"]["text"]
                    
            if result["dm"].get("command") is not None:
                datas[index_local_command] = format_reality_command(result["dm"]["command"])
            elif result["dm"].get("dataFrom") == "native":
                datas[index_local_command] = format_reality_command(result["dm"])
            elif result["dm"].get("inspire") is not None:
                datas[index_local_command] = format_reality_command_inspire(result["dm"]["inspire"])
            if result["dm"].get("nlg") is not None:
                datas[index_local_nlg] = result["dm"]["nlg"]
            if result["dm"].get("speak") is not None:
                datas[index_local_nlg] = result["dm"]["speak"]["text"]

            # 写入测试结果
            datas[index_local] = json.dumps(result, ensure_ascii=False)
        
with pd.ExcelWriter("本地对比-" + file_name) as writer:
    try:
        do_test()
    except Exception as e:
        print(e)
    # 回写数据结果到Excel文件
    df = pd.DataFrame(lines[1:], columns=file_head)
    df.to_excel(writer, sheet_name=sheet_name, index=False, header=True)
print("end time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print("测试完成！")
