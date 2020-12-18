'''
Author: your name
Date: 2020-12-14 15:36:03
LastEditTime: 2020-12-14 18:29:42
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \leetcodei:\python-workspace\awsome-python-web\www\test.py
'''
import asyncio
from os import name
from orm import create_pool
from models import User, Blog, Comment
from read_config import read_config

async def test(loop):
    conf=read_config()
    mysql_conf=conf.get("mysql",{})
    await create_pool(loop=loop,**mysql_conf)

    # u = User(name='Test', email='test@example13com', pwd='1234567890', avatar='about:blank')
    # await u.save()
    # u.email="961332109@qq.com"
    # await u.update()
    t= await User.findAll()
    for i in t:
        print(i)
        
    t1=await User.findNumber(selectField="count(id)")
    print(t1)



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [test(loop)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
