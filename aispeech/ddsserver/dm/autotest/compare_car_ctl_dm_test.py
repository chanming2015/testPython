#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2023-03-25

@author: XuMaosen
"""

import json

import pandas as pd
from base import compare_command_all, format_command_str, str_split_line

# 读取Excel文件测试数据
file_name = "极氪单轮车控测试集-标定对比结果.xlsx"
excel_file = pd.ExcelFile(file_name)


def compare_command_str(expect_str, reality_str, datas, index_error):
    command_map_expect = format_command_str(expect_str)
    command_map_reality = format_command_str(reality_str)
    return compare_command_all(command_map_expect, command_map_reality, datas, index_error)

with pd.ExcelWriter("测试结果-" + file_name) as writer:
    # 遍历所有工作表
    for sheet_name in excel_file.sheet_names:
        lines = pd.read_excel(file_name, sheet_name=sheet_name, header=None).values.tolist()
        file_head = lines[0]
        
        # 定义测试数据列索引
        index_refText = file_head.index("测试用例")
        index_error = file_head.index("错误提示")
        index_command = file_head.index("实际command")
        index_nlg = file_head.index("实际nlg")
        index_reality = file_head.index("实际结果")

        # 循环测试数据
        for datas in lines[1:]:
            expect = datas[file_head.index("command")]
            expect_nlg = datas[file_head.index("nlg")]  
            error = datas[index_error]
            command = datas[index_command]
            nlg = datas[index_nlg]
            reality = datas[index_reality]
            
            if type(datas[index_refText]) is not str or type(reality) is not str:
                continue

#             print(datas[index_refText])
            
            if reality.startswith("{") and reality.endswith("}"):
                jsob_reality = json.loads(reality).get('dm')
                if jsob_reality.get('widget') is not None:
                    del jsob_reality['widget']
                
                if "实际param1" in file_head and "实际api1" in file_head and "实际param2" in file_head and "实际api2" in file_head:
                    if type(command) is str:
                        # 预期是多意图指令
                        if command.find(str_split_line) > 0:
                            for index , cmd_str in enumerate(command.split(str_split_line)):
                                cmd = format_command_str(cmd_str)
                                datas[file_head.index("实际api" + str(index + 1))] = cmd['api']
                                datas[file_head.index("实际param" + str(index + 1))] = json.dumps(cmd['param'], ensure_ascii=False)
                        else:
                            cmd = format_command_str(command)
                            datas[file_head.index("实际api1")] = cmd['api']
                            datas[file_head.index("实际param1")] = json.dumps(cmd['param'], ensure_ascii=False)
                    
            
            if type(expect) is str: 
                # 预期有指令
                if expect.find("api=") < 0:
                    expect = "api=sys.car.crl\nparam.customInnerType=nativeCommand\n" + expect
                
                if expect.find(str_split_line) > 0:
                    # 预期是多意图指令
                    if type(command) is str and command.find(str_split_line) > 0:
                        # 实际是多意图指令
                        expect_commands = expect.split(str_split_line)
                        reality_commands = command.split(str_split_line)
                        if len(expect_commands) != len(reality_commands):
                            datas[index_error] = "预期是多意图，实际是多意图，但意图数量不一致"
                            continue
                        else:
                            for index, cmd in enumerate(expect_commands):
                                if not compare_command_str(cmd, reality_commands[index], datas, index_error):
                                    continue
                    else:
                        # 实际是单意图指令
                        datas[index_error] = "预期是多意图，实际是单意图"
                        continue
                else:
                    # 预期是单意图指令
                    if type(command) is str:
                        if command.find(str_split_line) > 0:
                            # 实际是多意图指令
                            datas[index_error] = "预期是单意图，实际是多意图"
                            continue
                        else:
                            # 实际是单意图指令
                            if not compare_command_str(expect, command, datas, index_error):
                                continue
                
                if type(command) is not str and type(nlg) is str:
                    datas[index_error] = "预期是command，实际是nlg"
                    continue
            else:
                # 预期没有指令
                if type(command) is str:
                    # 实际有指令
                    datas[index_error] = "预期没有指令，实际有指令"
                    continue
                # 预期有nlg，实际没有
                if type(expect_nlg) is str and type(nlg) is not str:
                    datas[index_error] = "预期有nlg，实际没有"
                    continue
                # 预期没有nlg，实际有
                if type(nlg) is str and type(expect_nlg) is not str:
                    datas[index_error] = "预期没有nlg，实际有"
                    continue

        # 回写数据结果到Excel文件
        df = pd.DataFrame(lines[1:], columns=file_head)
        df.to_excel(writer, sheet_name=sheet_name, index=False, header=True)
print("测试完成！")
