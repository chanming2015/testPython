#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2023-03-25

@author: XuMaosen
"""

import json

import pandas as pd

# 读取Excel文件测试数据
file_name = "多轮车控测试集-2月对比.xlsx"
sheet_name = "279606354-car_ctl_beta_test"
lines = pd.read_excel(file_name, sheet_name=sheet_name, header=None).values.tolist()
file_head = lines[0]

# 定义测试数据列索引
index_expect = file_head.index("2月标注结果")
index_error = file_head.index("错误提示")
index_command = file_head.index("实际command")
index_nlg = file_head.index("实际nlg")
index_reality = file_head.index("实际结果")

str_split_line = "--------------------"


def format_commands(commands=[]):
    # [param, action, 打开]  --> {'param': {'action': '打开'}}
    command_map = {}
    if len(commands) > 2:
        cmds = format_commands(commands[1:])
        command_map[commands[0]] = cmds
    elif len(commands) == 2:
        command_map[commands[0]] = commands[1]
    return command_map


def format_command_str(command_str):
    command_map = {}
    command_line = command_str.split("\n")
    for line in command_line:
        kv = line.split("=")
        if len(kv) == 2:
            if kv[0].find(".") > 0:
                commands = []
                commands += (kv[0].split("."))
                commands.append(kv[1])
                map_merge(command_map, format_commands(commands))
            else:
                command_map[kv[0]] = kv[1]
    return command_map


def map_merge(map1, map2):
    for key in map2:
        if key in map1:
            if type(map1[key]) is dict:
                map_merge(map1[key], map2[key])
            else:
                map1[key] = map2[key]
        else:
            map1[key] = map2[key]


def compare_command(expect_command, reality_command):
    continue_falg = True
    for k, v in expect_command.items():
        expect_command_value = v
        reality_command_value = reality_command.get(k)

        if type(v) is dict:
            for kk in v.keys():
                expect_command_value = expect_command.get(k, {}).get(kk)
                reality_command_value = reality_command.get(k, {}).get(kk)
                if expect_command_value != reality_command_value:
                    if 'param' == kk:
                        continue_falg = compare_command(expect_command_value, reality_command_value)
                        if not continue_falg:
                            break
                        else:
                            continue
                    elif 'part_raw' == kk:
                        if expect_command_value == reality_command.get(k, {}).get('part') or expect_command_value == reality_command.get(k, {}).get('feature'):
                            continue
                    elif 'object_raw' == kk:
                        if expect_command_value == reality_command.get(k, {}).get('object') or expect_command_value == reality_command.get(k, {}).get('light_type_inside'):
                            continue
                    elif 'light_type_inside' == kk or 'light_type_outside' == kk:
                        if expect_command_value == reality_command.get(k, {}).get('object'):
                            continue

                    continue_falg = False
                    datas[index_error] = "command错误，预期返回结果：%s=%s，实际返回结果：%s=%s" % (kk, expect_command_value, kk, reality_command_value)
                    break
            if not continue_falg:
                break
        elif expect_command_value != reality_command_value:
            continue_falg = False
            datas[index_error] = "command错误，预期返回结果：%s=%s，实际返回结果：%s=%s" % (k, expect_command_value, k, reality_command_value)
            break
    return continue_falg


# 循环测试数据
for datas in lines[1:]:
    expect = datas[index_expect]
    error = datas[index_error]
    command = datas[index_command]
    nlg = datas[index_nlg]
    reality = datas[index_reality]

    if type(expect) is str and expect.startswith("{") and expect.endswith("}") and reality.startswith("{") and reality.endswith("}"):
        jsob_expect = json.loads(expect)
        jsob_reality = json.loads(reality).get('dm')

        if jsob_expect.get('command') is not None:
            # 预期有command
            if jsob_reality.get('command') is not None:
                expect_command = jsob_expect.get('command')
                reality_command = jsob_reality.get('command')
                compare_command(expect_command, reality_command)
            else:
                datas[index_error] = "预期有command，实际不是"
                continue

        if jsob_expect.get('inspire') is not None:
            # 预期有inspire
            if jsob_reality.get('inspire') is not None:
                if len(jsob_expect.get('inspire')) != len(jsob_reality.get('inspire')):
                    datas[index_error] = "预期是多意图，实际是多意图，但意图数量不一致"
                    continue
                else:
                    for index, ins_expect in enumerate(jsob_expect.get('inspire')):
                        if type(datas[index_error]) is str and len(datas[index_error]) > 0:
                            break
                        ins_reality = jsob_reality.get('inspire')[index]
                        compare_command(ins_expect, ins_reality)
            else:
                datas[index_error] = "预期是多意图，实际不是"
                continue

        if len(jsob_expect.get('nlg')) > 0:
            # 预期有nlg
            if len(jsob_expect.get('nlg')) == 0:
                datas[index_error] = "预期有nlg，实际没有"
                continue
        else:
            # 预期没有nlg
            if len(jsob_expect.get('nlg')) > 0:
                datas[index_error] = "预期没有nlg，实际有"
                continue

    else:
        if type(expect) is str and expect.startswith("api=sys.car.crl"):
            # 预期是command
            if type(command) is not str and type(nlg) is str:
                datas[index_error] = "预期是command，实际是nlg"
                continue
            if type(command) is str:
                command_map_expect = format_command_str(expect)
                command_map_reality = format_command_str(command)
                if command_map_expect != command_map_reality:
                    compare_command(command_map_expect, command_map_reality)
        else:
            # 预期是nlg
            if type(nlg) is not str and type(command) is str:
                datas[index_error] = "预期是nlg，实际是command"
                continue

# 回写数据结果到Excel文件
df = pd.DataFrame(lines[1:], columns=file_head)
df.to_excel("测试结果-" + file_name, sheet_name=sheet_name, index=False, header=True)
print("测试完成！")
