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

from base import format_reality_nlu, parse_reality_nlu, format_reality_command, format_reality_command_inspire, format_command_str, format_inspire_str, compare_command, str_split_line, textRequest

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
excel_file = pd.ExcelFile(file_name)

# 执行webSocket请求，执行测试
async def do_test(lines_data):
    session_id = uuid4().hex
    print("start time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # 打印webSocket连接地址
    print("webSocket连接地址：%s" % SERVER_URL)
    # 创建webSocket连接
    async with websockets.connect(SERVER_URL, ping_interval=None, ping_timeout=None) as websocket:
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
                if type(datas[index_reality_command]) is not str or datas[index_reality_command].strip() == "":
                    datas[index_error_message] = "command错误，预期返回结果：有，实际返回结果：无"
                    continue

                if datas[index_command].find(str_split_line) > 0:
                    # 预期有inspire
                    if result["dm"].get('inspire') is not None:
                        inspire = format_inspire_str(datas[index_command])
                        if len(inspire) != len(result["dm"].get('inspire')):
                            datas[index_error_message] = "预期是多意图，实际是多意图，但意图数量不一致"
                            continue
                        else:
                            for index, ins_expect in enumerate(inspire):
                                if type(datas[index_error_message]) is str and len(datas[index_error_message]) > 0:
                                    break
                                ins_reality = inspire[index]
                                compare_command(ins_expect, ins_reality, datas, index_error_message)
                    else:
                        datas[index_error_message] = "预期是多意图，实际不是"
                        continue
                else:
                    # 预期有command
                    if result["dm"].get('command') is not None:
                        expect_command = format_command_str(datas[index_command])
                        reality_command = result["dm"].get('command')
                        compare_command(expect_command, reality_command, datas, index_error_message)
                    else:
                        datas[index_error_message] = "预期有单意图command，实际不是"
                        continue
            else:
                if type(datas[index_reality_command]) is str and datas[index_reality_command].strip() != "":
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


with pd.ExcelWriter("测试结果-" + file_name) as writer:
    # 遍历所有工作表
    for sheet_name in excel_file.sheet_names:
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
        
        try:
            asyncio.get_event_loop().run_until_complete(do_test(lines))
        except Exception as e:
            print(e)

        # 回写数据结果到Excel文件
        df = pd.DataFrame(lines[1:], columns=file_head)
        df.to_excel(writer, sheet_name=sheet_name, index=False, header=True)
    
print("end time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print("测试完成！")
