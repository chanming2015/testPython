#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2023-03-25

@author: XuMaosen
"""

import json

import pandas as pd
from base import compare_command, format_command_str

# 读取Excel文件测试数据
file_name = "单轮车控测试集-2月对比.xlsx"
excel_file = pd.ExcelFile(file_name)

with pd.ExcelWriter("测试结果-" + file_name) as writer:
    # 遍历所有工作表
    for sheet_name in excel_file.sheet_names:
        lines = pd.read_excel(file_name, sheet_name=sheet_name, header=None).values.tolist()
        file_head = lines[0]
        
        # 定义测试数据列索引
        index_expect = file_head.index("2月标注结果")
        index_error = file_head.index("错误提示")
        index_command = file_head.index("实际command")
        index_nlg = file_head.index("实际nlg")
        index_reality = file_head.index("实际结果")

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
                        compare_command(expect_command, reality_command, datas, index_error)
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
                                compare_command(ins_expect, ins_reality, datas, index_error)
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
                            compare_command(command_map_expect, command_map_reality, datas, index_error)
                else:
                    # 预期是nlg
                    if type(nlg) is not str and type(command) is str:
                        datas[index_error] = "预期是nlg，实际是command"
                        continue

        # 回写数据结果到Excel文件
        df = pd.DataFrame(lines[1:], columns=file_head)
        df.to_excel(writer, sheet_name=sheet_name, index=False, header=True)
print("测试完成！")
