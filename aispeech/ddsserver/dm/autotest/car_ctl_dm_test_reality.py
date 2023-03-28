#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2023-03-25

@author: XuMaosen
"""

import pandas as pd
import requests

# 设置产品ID
PRODUCT_ID = "279606354"
# 设置分支
BRANCH = "prod_p11"
# 设置授权APIKEY；DUI开放平台-授权管理
APIKEY = ""
# 参数非空校验
if PRODUCT_ID == "" or BRANCH == "" or APIKEY == "":
    print("请设置产品ID、分支、授权APIKEY！")
    exit(1)
# 定义测试服务地址
SERVER_URL = "https://dds.dui.ai/dds/v3/%s?productId=%s&apikey=%s&deviceName=carCtlDmTestAutoTest&communicationType=fullDuplex" % (BRANCH, PRODUCT_ID, APIKEY)
# 读取Excel文件测试数据，每个测试用例按照单轮执行
file_name = "车控测试集2.xlsx"
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


# 循环测试数据
for datas in lines[1:]:
    # 获取测试用例
    refText = datas[index_refText]
    print("测试用例：%s" % refText)
    # 构造请求参数
    data = {"topic": "nlu.input.text", "refText": refText}
    # 调用测试服务地址
    resp = requests.post(SERVER_URL, json=data, timeout=10);
    if resp.status_code != 200:
        datas[index_error_message] = "请求失败，状态码：%s" % resp.status_code
        print("请求失败，状态码：%s" % resp.status_code)
        break
    # 解析测试返回结果
    result = resp.json()

    # 写入测试结果
    # datas[index_reality] = resp.text
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

# 回写数据结果到Excel文件
df = pd.DataFrame(lines[1:], columns=file_head)
df.to_excel("测试结果-" + file_name, sheet_name="%s-%s-%s" % (sheet_name, PRODUCT_ID, BRANCH), index=False, header=True)
print("测试完成！")
