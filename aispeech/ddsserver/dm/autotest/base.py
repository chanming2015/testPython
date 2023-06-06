'''
Created on 2023年4月14日

@author: Administrator
'''
import json
# import time
from uuid import uuid4

str_split_line = "--------------------"


# 解析实际语义函数
def parse_reality_nlu(nlu):
    reality_nlu_map = {}
    if nlu.get("semantics") is not None:
        for slot in nlu["semantics"]["request"]["slots"]:
            reality_nlu_map[slot["name"]] = slot["value"]
            if slot.get("rawvalue") is not None:
                reality_nlu_map[slot["name"] + "_raw"] = slot["rawvalue"]
    return reality_nlu_map


# 格式化实际语义，换行显示
def format_reality_nlu(nlu):
    reality_nlu = []
    if nlu.get("semantics") is not None:
        for slot in nlu["semantics"]["request"]["slots"]:
            if "intent" == slot["name"]:
                if len(reality_nlu) > 0 and str_split_line != reality_nlu[0]:
                    reality_nlu.insert(0, str_split_line)
                else:
                    reality_nlu.append(str_split_line)
            else:
                reality_nlu.append(slot["name"] + "=" + slot["value"])
                if slot.get("rawvalue") is not None:
                    reality_nlu.append(slot["name"] + "_raw=" + slot["rawvalue"])
        if len(reality_nlu) > 0 and str_split_line == reality_nlu[0]:
            reality_nlu = reality_nlu[1:]
    return "\n".join(reality_nlu)


# 格式化实际command，换行显示
def format_reality_command(command):
    reality_command = ["api=" + command["api"]]
    if command.get("param") is not None:
        for k, v in command["param"].items():
            reality_command.append("param." + k + "=" + v)
    return "\n".join(reality_command)


# 格式化实际inspire command，换行显示
def format_reality_command_inspire(inspire):
    reality_command = []
    for ins in inspire:
        if ins.get('command') is not None:
            reality_command.append(str_split_line)
            reality_command.append(format_reality_command(ins['command']))
    if len(reality_command) > 0 and str_split_line == reality_command[0]:
        reality_command = reality_command[1:]
    return "\n".join(reality_command)


def format_commands(commands=[]):
    # [param, action, 打开]  --> {'param': {'action': '打开'}}
    command_map = {}
    if len(commands) > 2:
        cmds = format_commands(commands[1:])
        command_map[commands[0].strip()] = cmds
    elif len(commands) == 2:
        command_map[commands[0].strip()] = commands[1].strip()
    return command_map


def format_command_str(command_str):
    command_map = {}
    command_line = command_str.split("\n")
    for line in command_line:
        if not line.startswith("api=") and not line.startswith("param."):
            line = "param." + line
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


def format_inspire_str(command_str):
    command_list = []
    for cm in command_str.split(str_split_line):
        command_list.append(format_command_str(cm))
    return command_list


def map_merge(map1, map2):
    for key in map2:
        if key in map1:
            if type(map1[key]) is dict:
                map_merge(map1[key], map2[key])
            else:
                map1[key] = map2[key]
        else:
            map1[key] = map2[key]

def compare_command_all(expect_command, reality_command, datas, index_error):
    if compare_command(expect_command, reality_command, datas, index_error):
        return compare_command(reality_command, expect_command, datas, index_error, False)
    
def compare_command(expect_command, reality_command, datas, index_error, formart_flag=True):
    formart_str = "command错误，预期返回结果：%s=%s，实际返回结果：%s=%s" if formart_flag else "command错误，实际返回结果：%s=%s，预期返回结果：%s=%s"
    continue_falg = True
    for k, v in expect_command.items():
        if 'endSkillDm' == k or 'widget'==k:
            continue
        expect_command_value = v
        reality_command_value = reality_command.get(k)

        if type(v) is dict:
            for kk in v.keys():
                expect_command_value = expect_command.get(k, {}).get(kk)
                reality_command_value = reality_command.get(k, {}).get(kk)
                if expect_command_value != reality_command_value:
                    if 'param' == kk:
                        continue_falg = compare_command(expect_command_value, reality_command_value, datas, index_error, formart_flag)
                        if not continue_falg:
                            break
                        else:
                            continue
#                     elif 'part_raw' == kk:
#                         if expect_command_value == reality_command.get(k, {}).get('part') or expect_command_value == reality_command.get(k, {}).get('feature'):
#                             continue
#                     elif 'object_raw' == kk:
#                         if expect_command_value == reality_command.get(k, {}).get('object') or expect_command_value == reality_command.get(k, {}).get('light_type_inside'):
#                             continue
#                     elif 'light_type_inside' == kk or 'light_type_outside' == kk:
#                         if expect_command_value == reality_command.get(k, {}).get('object'):
#                             continue

                    if not formart_flag and reality_command_value is None:
                        if 'page_raw' == kk:
                            continue
                    continue_falg = False
                    datas[index_error] = formart_str % (kk, expect_command_value, kk, reality_command_value)
                    break
            if not continue_falg:
                break
        elif expect_command_value != reality_command_value:
            continue_falg = False
            datas[index_error] = formart_str % (k, expect_command_value, k, reality_command_value)
            break
    return continue_falg


async def textRequest(ws, refText, sessionId=None):
#     time.sleep(0.2)
    # 构造请求参数
    content = {
        "topic": 'nlu.input.text',
        "recordId": uuid4().hex,
        "refText": refText
    }
    if sessionId is not None:
        content["sessionId"] = sessionId
    try:
        # 发送请求
        print("请求参数：%s" % json.dumps(content, ensure_ascii=False))
        await ws.send(json.dumps(content))
        # 接收响应
        resp = await ws.recv()
        # print("响应结果：%s" % resp)
        return resp
    except websockets.WebSocketException as exp:
        print(exp)


async def systemSetting(ws):
    # 做技能级配置。
    content = {
        "topic": "system.settings",
        "settings": [
            {
                "key": "filterSwitch",
                "value": "off"
            }
        ]
    }
    try:
        await ws.send(json.dumps(content))
        resp = await ws.recv()
        print(resp)
    except websockets.WebSocketException as exp:
        print(exp)
