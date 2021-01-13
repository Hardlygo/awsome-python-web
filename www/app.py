'''
Author: your name
Date: 2020-12-10 17:33:48
LastEditTime: 2021-01-12 22:44:20
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \leetcodei:\python-workspace\awsome-python-web\www\app.py
'''
import re
import time
import json
import os
import asyncio
from coroweb import get, add_route,add_routes,add_static
from read_config import read_config
from models import User, Blog, Comment
from orm import create_pool
from handlers import cookie2user, COOKIE_NAME
from aiohttp import web
from datetime import datetime
import logging

from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.DEBUG)


def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env


# 构造返回的中间件
async def response_factory(app, handler):
    async def response(request):
        # logging.log(msg='response handler')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            # 本来就是一个web.response类型
            return r
        if isinstance(r, bytes):
            # 文本文件类型
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            # 重定向
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get("__template__")
            if template is None:
                # restful api返回
                resp = web.Response(body=json.dumps(
                    r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                # 返回本地页面
                r['__user__'] = request.__user__
                resp = web.Response(body=app['__templating__'].get_template(
                    template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r >= 100 and r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(t, str(m))
         # default:
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp

    return response


async def logger_factory(app, handler):
    """
    打印中间件
    """
    async def logger(request):
        logging.info("Request %s %s" % (request.method, request.path))
        return (await handler(request))

    return logger


async def data_factory(app, handler):
    '''
    获取入参中间件
    '''
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith("application/json"):
                request.__data__ = await request.json()
                logging.info('request json: %s' % str(request.__data__))
            elif request.content_type.startswith("application/x-www-form-urlencoded"):
                request.__date__ = await request.post()
                logging.info('request form: %s' % str(request.__data__))
        return await handler(request)
    return parse_data


async def auth_factory(app, handler):
    async def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str:
            user = await cookie2user(cookie_str)
            if user:
                logging.info('set current user: %s' % user.email)
                request.__user__ = user
        if request.path.startswith('/manage/'):
            if request.__user__ is None:
                return web.HTTPFound('/signin')
            if not request.__user__.admin:
                return web.HTTPFound('/no-auth')
        return (await handler(request))
    return auth


def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


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
    app = web.Application(middlewares={
        logger_factory, auth_factory, response_factory
    })

    # 连接数据库配置开始
    conf = read_config()
    mysql_conf = conf.get("mysql", {})
    await create_pool(loop=loop, **mysql_conf)
    # 连接数据库配置结束
    # app.router.add_route("GET","/",index)
    # add_route(app=app, fn=index)
    # add_route(app=app, fn=home)
    # svr = await loop.create_server(app.make_handler(), "127.0.0.1", 9000)
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    add_routes(app, 'handlers')
    add_static(app)
    app_runner = web.AppRunner(app)
    await app_runner.setup()

    svr = await loop.create_server(app_runner.server, "127.0.0.1", 9000)
    logging.info("starting server at 127.0.0.1:9000...")
    return svr

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
