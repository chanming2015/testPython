#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2023-03-25

@author: XuMaosen
"""
import json

import pandas as pd
import requests

# 设置产品ID
PRODUCT_ID = "279606354"
# 设置分支
BRANCH = "prod_p11"
# 设置授权APIKEY
APIKEY = ""
# 参数非空校验
if PRODUCT_ID == "" or BRANCH == "" or APIKEY == "":
    print("请设置产品ID、分支、授权APIKEY！")
    exit(1)
# 定义测试服务地址
SERVER_URL = "https://dds.dui.ai/dds/v3/%s?productId=%s&apikey=%s&deviceName=carCtlDmTestAutoTest&communicationType=fullDuplex" % (BRANCH, PRODUCT_ID, APIKEY)
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
index_error_message = file_head.index("错误提示")
index_reality = file_head.index("实际结果")


# 解析实际语义函数
def parse_reality_nlu(nlu):
    reality_nlu_map = {}
    for slot in nlu["semantics"]["request"]["slots"]:
        reality_nlu_map[slot["name"]] = slot["value"]
    return reality_nlu_map


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
    # 解析返回结果
    result = resp.json()
    datas[index_reality] = resp.text
    # 比较技能、任务、意图、语义、command
    if datas[index_skill].strip() != "" and datas[index_skill] != result["skill"]:
        datas[index_error_message] = "技能错误，返回结果：%s" % result["skill"]
        continue
    if datas[index_task].strip() != "" and datas[index_task] != result["dm"]["task"]:
        datas[index_error_message] = "任务错误，返回结果：%s" % result["dm"]["task"]
        continue
    if datas[index_intent].strip() != "" and datas[index_intent] != result["dm"]["intentName"]:
        datas[index_error_message] = "意图错误，返回结果：%s" % result["dm"]["intentName"]
        continue
    if datas[index_nlu].strip() != "":
        if result.get("nlu") is None:
            datas[index_error_message] = "语义错误，返回结果：无"
            continue
        reality_nlu = parse_reality_nlu(result["nlu"])
        for kv_str in datas[index_nlu].strip().split("&"):
            kvs = kv_str.split("=")
            if kvs[1] != reality_nlu.get(kvs[0]):
                datas[index_error_message] = "语义错误，返回结果：%s" % json.dumps(reality_nlu, ensure_ascii=False)
                break
    if datas[index_command].strip() != "":
        command = json.loads(datas[index_command])
        if command != result["dm"]["command"]:
            datas[index_error_message] = "command错误，返回结果：%s" % json.dumps(result["dm"]["command"], ensure_ascii=False)
            continue

# 回写数据结果
df = pd.DataFrame(lines[1:], columns=file_head)
df.to_excel("测试结果-" + file_name, sheet_name=sheet_name, index=False, header=True)
print("测试完成！")
