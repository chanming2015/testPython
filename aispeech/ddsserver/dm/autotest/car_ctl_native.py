#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2023-07-17

@author: XuMaosen
"""
import asyncio
import websockets
from uuid import uuid4
from base import textRequest, dmInputData

SERVER_URL = "wss://dds.dui.ai/dds/v3/%s?serviceType=websocket&productId=%s&apikey=%s&deviceName=geelyIntelligentDriveAutoTest&communicationType=fullDuplex" % ('car_ctl_beta_test', '279615509', '')

async def do_test():
    async with websockets.connect(SERVER_URL, ping_interval=None, ping_timeout=None) as websocket:
        session_id = uuid4().hex
        print(await textRequest(websocket, "打开定速巡航", session_id))
        print(await dmInputData(websocket, "native://sys.native.car.crl", {"outputcmd":0, "cancelcmd":1}, session_id))
        print(await textRequest(websocket, "啦啦啦", session_id))
        print(await textRequest(websocket, "取消", session_id))
        print(await textRequest(websocket, "确认", session_id))
#         await textRequest(websocket, "再大一点", session_id)        # 二轮询问？
#         await textRequest(websocket, "取消", session_id)           # 
#         await textRequest(websocket, "再大一点", session_id)
        
#         session_id = uuid4().hex
#         await textRequest(websocket, "音量调到80%", session_id)
#         await dmInputData(websocket, "native://sys.native.car.crl", {"outputcmd":1}, session_id)
        
#         session_id = uuid4().hex
#         await textRequest(websocket, "音量调到80%", session_id)
#         await dmInputData(websocket, "native://sys.native.car.crl", {"code":0.9}, session_id)
        print("测试完成！")
        
if __name__ == '__main__':            
    try:
        asyncio.get_event_loop().run_until_complete(do_test())
    except Exception as e:
        print(e)
    
