#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2023-03-25

@author: XuMaosen
"""

import json

import pandas as pd
from base import compare_command, compare_command_all, format_command_str

# 读取Excel文件测试数据
file_name = "长城单轮车控测试集-标定对比.xlsx"
excel_file = pd.ExcelFile(file_name)

with pd.ExcelWriter("测试结果-" + file_name) as writer:
    # 遍历所有工作表
    for sheet_name in excel_file.sheet_names:
        lines = pd.read_excel(file_name, sheet_name=sheet_name, header=None).values.tolist()
        file_head = lines[0]
        
        # 定义测试数据列索引
        index_refText = file_head.index("测试用例")
        index_expect = file_head.index("command")
        index_error = file_head.index("错误提示")
        index_command = file_head.index("实际command")
        index_nlg = file_head.index("实际nlg")
        index_reality = file_head.index("实际结果")
        index_reality_dm = file_head.index("实际DM")

        # 循环测试数据
        for datas in lines[1:]:
            expect = datas[index_expect]
            error = datas[index_error]
            command = datas[index_command]
            nlg = datas[index_nlg]
            reality = datas[index_reality]
            
            if type(datas[index_refText]) is not str:
                continue
            
            if reality.startswith("{") and reality.endswith("}"):
                jsob_reality = json.loads(reality).get('dm')
                datas[index_reality_dm] = json.dumps(jsob_reality, ensure_ascii=False)
            
            if type(expect) is not str:
                expect = datas[index_reality_dm]
                datas[index_expect] = expect
        
            if type(expect) is str and expect.startswith("{") and expect.endswith("}"):
                jsob_expect = json.loads(expect)
                
                if jsob_expect.get('dm') is not None:
                    jsob_expect = jsob_expect.get('dm')
                
                if jsob_expect.get('customInnerType') is not None:
                    nlg = ""
                    if jsob_expect.get('vague_type_cmd') is not None:
                        nlg = "模糊指令NLG"
                    jsob_expect = {"command":{"api": "sys.car.crl", "param":jsob_expect}, "nlg":nlg}
        
                if jsob_expect.get('command') is not None:
                    # 预期有command
                    if jsob_reality.get('command') is not None:
                        expect_command = jsob_expect.get('command')
                        reality_command = jsob_reality.get('command')
                        compare_command_all(expect_command, reality_command, datas, index_error)
#                         if compare_command(expect_command, reality_command, datas, index_error):
#                             datas[index_expect] = datas[index_reality_dm]
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
                                if not compare_command_all(ins_expect.get('command'), ins_reality.get('command'), datas, index_error):
                                    break
                    else:
                        datas[index_error] = "预期是多意图，实际不是"
                        continue
        
                if jsob_expect.get('nlg') is not None and len(jsob_expect.get('nlg')) > 0:
                    # 预期有nlg
                    if jsob_reality.get('nlg') is None or len(jsob_reality.get('nlg')) == 0:
                        datas[index_error] = "预期有nlg，实际没有"
                        continue
                else:
                    # 预期没有nlg
                    if jsob_reality.get('nlg') is not None and len(jsob_reality.get('nlg')) > 0:
                        datas[index_error] = "预期没有nlg，实际有"
                        continue
        
            else:
                if type(expect) is str and expect.startswith("api="):
                    # 预期是command
                    if type(command) is not str and type(nlg) is str:
                        datas[index_error] = "预期是command，实际是nlg"
                        continue
                    if type(command) is str:
                        command_map_expect = format_command_str(expect)
                        command_map_reality = format_command_str(command)
                        if command_map_expect != command_map_reality:
                            compare_command_all(command_map_expect, command_map_reality, datas, index_error)
                else:
                    # 预期是nlg
                    if type(nlg) is not str and type(command) is str:
                        datas[index_error] = "预期是nlg，实际是command"
                        continue

        # 回写数据结果到Excel文件
        df = pd.DataFrame(lines[1:], columns=file_head)
        df.to_excel(writer, sheet_name=sheet_name, index=False, header=True)
print("测试完成！")
