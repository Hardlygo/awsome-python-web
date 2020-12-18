'''
Author: your name
Date: 2020-12-10 17:33:48
LastEditTime: 2020-12-17 22:54:18
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \leetcodei:\python-workspace\awsome-python-web\www\app.py
'''
import time
import json
import os
import asyncio
from coroweb import get, add_route
from read_config import read_config
from models import User, Blog, Comment
from orm import create_pool
from aiohttp import web
from datetime import datetime
import logging

import inspect
logging.basicConfig(level=logging.INFO)

@get('/home')
def home(request):
    return web.Response(body=b"<h1>Awsome</h1>", headers={'content-type': 'text/html'})


@get('/')
async def index(request):
    users = await User.findAll()
    resp = web.Response(body=json.dumps(dict(
        user=users), ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
    resp.content_type = 'application/json;charset=utf-8'
    return resp


async def init(loop):
    app = web.Application()

    # 连接数据库配置开始
    conf = read_config()
    mysql_conf = conf.get("mysql", {})
    await create_pool(loop=loop, **mysql_conf)
    # 连接数据库配置结束
    # app.router.add_route("GET","/",index)
    add_route(app=app, fn=index)
    add_route(app=app, fn=home)
    # svr = await loop.create_server(app.make_handler(), "127.0.0.1", 9000)
    app_runner = web.AppRunner(app) 
    await app_runner.setup()
    svr = await loop.create_server(app_runner.server, "127.0.0.1", 9000)
    logging.info("starting server at 127.0.0.1:9000...")
    return svr

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
