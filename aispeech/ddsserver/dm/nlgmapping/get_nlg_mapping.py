#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2024年5月9日

@author: XuMaosen
'''
import pandas as pd
from _functools import reduce
import json

def dict_merge(dict1 , dict2):
    dict1.update(dict2)
    return dict1

file_name = "NLG-279619548-20240701.xlsx"
excel_file = pd.ExcelFile(file_name)

nlg_mappings = {}
# 遍历所有工作表
for sheet_name in excel_file.sheet_names:
    nlg_mapping = {}
    lines = pd.read_excel(file_name, sheet_name=sheet_name, header=None).values.tolist()
    file_head = list(map(lambda x:x.lower().replace('-', '_') if type(x) == str else x, lines[0]))
    
    if "nlg" not in file_head or "nlg_id" not in file_head:
        continue
#     print(sheet_name)
    # 获取NLG和ID的数据
    index_nlg = file_head.index("nlg")
    index_nlg_id = file_head.index("nlg_id")
    
    for datas in lines[1:]:
        # 判断同一个sheet中是否存在相同的nlg_id
        if type(datas[index_nlg_id]) != str:
            continue
        if nlg_mapping.get(datas[index_nlg_id]):
            print("sheet_name: %s 存在相同的nlg_id: %s" % (sheet_name, datas[index_nlg_id]))
#             break
        nlg_mapping[datas[index_nlg_id]] = datas[index_nlg]
    
    nlg_mappings[sheet_name] = nlg_mapping
    # 判断所有sheet中是否存在相同的nlg_id
    for sheet, nlg_mapping_sheet in nlg_mappings.items():
        if sheet != sheet_name:
            intersection = list(set(nlg_mapping.keys()) & set(nlg_mapping_sheet.keys()))
            if len(intersection) > 0:
                print("sheet_name: %s 、 %s 存在相同的nlg_id: %s" % (sheet, sheet_name, intersection))
                break

print(json.dumps(reduce(dict_merge, nlg_mappings.values()), ensure_ascii=False))
