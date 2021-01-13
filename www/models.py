'''
Author: your name
Date: 2020-12-14 09:38:11
LastEditTime: 2021-01-13 10:46:58
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \leetcodei:\python-workspace\awsome-python-web\www\models.py
models for user blog comment
'''
import time
import uuid

# vscode 只认项目目录的第一层所以要用www.orm
from orm import Model, StringField, BooleanField, IntegerField, TextField, FloatField


def next_id():  # 用时间和uuid生成id
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    '''
    users表的映射类
    '''
    __table__ = 'users'
    id = StringField("id", default=next_id, primary_key=True,
                     column_type="varchar(50)")
    email = StringField("email", column_type="varchar(50)")
    pwd = StringField("pwd", column_type="varchar(50)")
    name = StringField("name", column_type="varchar(50)")
    admin = BooleanField("admin")
    avatar = StringField("avatar", column_type="varchar(500)")
    created_at = FloatField("created_at", default=time.time)


class Blog(Model):
    '''
    blogs表的映射类
    '''
    __table__ = 'blogs'
    __autoIncreament__ = True
    id = IntegerField("id", primary_key=True, column_type="int(11)")
    user_id = StringField("user_id", column_type="varchar(50)")
    user_name = StringField("user_name", column_type="varchar(50)")
    user_avatar = StringField("user_avatar", column_type="varchar(500)")
    title = StringField("title", column_type="varchar(50)")
    summary = StringField("summary", column_type="varchar(200)")
    content = TextField("content")
    created_at = FloatField("created_at", default=time.time)


class Comment(Model):
    '''
   comments表的映射类
    '''
    __table__ = 'comments'

    id = StringField("id", default=next_id, primary_key=True,
                     column_type="varchar(50)")
    blog_id = StringField("blog_id", column_type="varchar(50)")
    user_id = StringField("user_id", column_type="varchar(50)")
    user_name = StringField("user_name", column_type="varchar(50)")
    user_avatar = StringField("user_avatar", column_type="varchar(500)")
    content = TextField("content")
    created_at = FloatField("created_at", default=time.time)
