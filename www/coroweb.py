'''
Author: your name
Date: 2020-12-14 21:29:39
LastEditTime: 2021-01-13 21:36:24
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \leetcodei:\python-workspace\awsome-python-web\www\coroweb.py
web方法解析
web方法参数处理
'''
import functools
import inspect
import os
import logging
import asyncio

from urllib import parse
from aiohttp import web

from api_error import APIError


# def get(path):
#     '''
#     get 方法的装饰器
#     '''
#     def decorator(func):
#         @functools.wraps(func)
#         async def wrraper(*args, **kw):
#             if not asyncio.iscoroutinefunction(func) and not inspect.isgeneratorfunction(func):
#                 return func(*args, **kw)
#             else:
#                 return await func(*args, **kw)
#         wrraper.__method__ = "GET"
#         wrraper.__route__ = path

#         return wrraper
#     return decorator


def get(path):
    '''
    get 方法的装饰器
    '''
    def decorator(func):
        if not asyncio.iscoroutinefunction(func) and not inspect.isgeneratorfunction(func):
            @functools.wraps(func)
            def wrraper(*args, **kw):
                return func(*args, **kw)
        else:
            @functools.wraps(func)
            async def wrraper(*args, **kw):
                return await func(*args, **kw)

        wrraper.__method__ = "GET"
        wrraper.__route__ = path

        return wrraper
    return decorator


def post(path):
    '''
    post 方法的装饰器
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrraper(*args, **kw):
            return func(*args, **kw)
        wrraper.__method__ = "POST"
        wrraper.__route__ = path
        return wrraper
    return decorator


def get_required_kw_args(fn):
    '''
    取得fn里面的出现在*或者*args之后的不为空关键字参数
    返回元组
    '''
    args = []
    params = inspect.signature(fn).parameters  # 函数签名字典
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            # 找出关键字参数且关键字参数没有默认值
            args.append(name)
    return tuple(args)


def get_named_kw_args(fn):
    '''
    取得fn里面的出现在*或者*args之后的关键字参数
    返回元组
    '''
    args = []
    params = inspect.signature(fn).parameters  # 函数签名字典
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            # 找出关键字参数且关键字参数没有默认值
            args.append(name)
    return tuple(args)


def has_named_kw_args(fn):
    '''
    判断fn里面是否存在出现在*或者*args之后的关键字参数
    返回bool
    '''
    params = inspect.signature(fn).parameters  # 函数签名字典
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True


def has_var_kw_args(fn):
    '''
    判断fn里面是否存在kw字典参数
    返回bool
    '''
    params = inspect.signature(fn).parameters  # 函数签名字典
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True


def has_request_arg(fn):
    # 判断是否存在request属性参数
    params = inspect.signature(fn).parameters  # 函数签名字典
    founded = False
    for name, param in params.items():
        if name == 'request':
            founded = True
            continue
        if founded and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            # request既不是位置参数也不是可变参数也不是关键字参数则报错
            raise ValueError('request parameter must be the last named parameter in function: %s%s' % (
                fn.__name__, str(inspect.signature(fn))))

    return founded


class RequestHandler(object):
    def __init__(self, app, fn):
        # print("处理函数", fn.__name__)
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._has_var_kw_args = has_var_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):
        kw = None
        if self._has_var_kw_args or self._has_named_kw_args or self._required_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-Type')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest("Json must be an object")
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest("Unsupported content-type:%s" % request.content_type)
            elif request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_args and self._named_kw_args:
                # remove all unamed kw:
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy

            # check named arg:
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning(
                        'Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v

        if self._has_request_arg:
            kw['request'] = request

        # check required kw:
        if self._required_kw_args:
            for name in self._required_kw_args:
                if not name in kw:
                    return web.HTTPBadRequest('Missing argument: %s' % name)

        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


def add_static(app):
    """
    指定应用的静态文件夹
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))


def add_route(app, fn):
    '''
    为应用增加单个路由
    '''
    # fn指向的路由处理方法
    method = getattr(fn, '__method__', None)
    # fn指向的路由路径
    route = getattr(fn, '__route__', None)

    if not method or not route:
        raise ValueError('@get or @post not defined in %s.' % str(fn))

    # print("%s是async函数吗？" % fn.__name__,
    #       "是" if inspect.iscoroutinefunction(fn) else "否")
    # if not asyncio.iscoroutinefunction(fn):
    #     fn = asyncio.coroutine(method)
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        #判断是否是async修饰的异步方法，不是的话转为异步
        fn = asyncio.coroutine(fn)

    # if not inspect.iscoroutinefunction(fn):
    #     raise ValueError('Function must be decorated by "async"')

    logging.info('add route %s %s => %s(%s)' % (
        method, route, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, route, RequestHandler(app, fn))


def add_routes(app, module_name):
    '''
    为应用增加多个路由
    '''
    n = module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n+1:]
        mod = getattr(__import__(
            module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        if attr.startswith("_"):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            method = getattr(fn, '__method__', None)
            route = getattr(fn, '__route__', None)
            if method and route:
                add_route(app, fn)
