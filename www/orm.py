'''
Author: your name
Date: 2020-12-11 11:02:42
LastEditTime: 2020-12-14 19:29:49
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \leetcodei:\python-workspace\awsome-python-web\www\orm.py
'''
# 参考网站 https://github.com/michaelliao/awesome-python3-webapp/blob/day-03/www/orm.py
# https://www.yangyanxing.com/article/aiomysql_in_python.html
#
import asyncio
import logging
import aiomysql


def log(sql, args=()):
    """
    打印sql输出
    """
    logging.info("SQL:%s" % sql)


async def create_pool(loop, **kw):
    logging.info("creating database connecttion pool ...")
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get("host"),
        port=kw.get("port", 3306),
        user=kw.get("user"),
        password=kw.get("password"),
        db=kw.get("db"),
        charset=kw.get("charset", "utf8"),
        autocommit=kw.get("autocommit", True),
        maxsize=kw.get("maxsize", 5),
        minsize=kw.get("minisize", 1),
        loop=loop
    )


async def select(sql, args, size=None):
    # 执行select语句
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace("?", "%s"), args or ())  # 问号用%s代替
            if size == None:
                rs = await cur.fetchall()
            else:
                rs = await cur.fetchmany(size)
        logging.info("rows returned:%s" % len(rs))
        return rs


async def execute(sql, args, autocommit=True):
    # 通用的execute()函数，执行INSERT、UPDATE、DELETE语句
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace("?", "%s"), args or ())
                affected = cur.rowcount
            if not autocommit:
                conn.commit()
        except BaseException as e:
            if not autocommit:
                conn.rollback()

            raise
        return affected

# 描述字段类型属性


class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name  # 字段名称
        self.column_type = column_type  # 字段类型
        self.primary_key = primary_key  # 是否主键
        self.default = default  # 字段默认值

    def __str__(self):
        return "<%s,%s:%s>" % (self.__class__.__name__, self.column_type, self.name)


class StringField(Field):
    def __init__(self, name=None, column_type="varchar(100)", primary_key=False, default=None):
        super().__init__(name, column_type, primary_key, default)


class BooleanField(Field):
    def __init__(self, name,  default=False):
        super().__init__(name, "boolean", False, default)


class IntegerField(Field):
    def __init__(self, name=None, column_type="bigint", primary_key=False, default=0):
        super().__init__(name, column_type, primary_key, default)


class TextField(Field):
    def __init__(self, name=None,  default=None):
        super().__init__(name, 'text', False, default)


class FloatField(Field):
    def __init__(self, name=None, default=0.0):
        super().__init__(name, "real", False, default)


def create_args_string(nums):
    l = []
    for n in range(nums):
        l.append("?")
    return ",".join(l)


def to_bool(value):
    """
    Converts 'something' to boolean. Raises exception for invalid formats
    Possible True values: 1, True,"1","TRue","yes","y","t"
    Possible False values: 0, False, None, [], {},"","0","faLse","no","n","f", 0.0,.. .
    """
    if str(value).lower() in ("yes", "y", "true", "t", "1"):
        return True
    if str(value).lower() in ("no", "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))


class ModelMetaclass(type):
    # 一个与数据库表映射的实体
    def __new__(cls, name, bases, attrs):#attrs是个dict
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)
        tabelName = attrs.get("__table__", None) or name
        autoIncreament = attrs.get(
            "__autoIncreament__", False)  # 如果配置了主键自动增长则设置为True,默认是False
        autoIncreament=to_bool(autoIncreament)#将其转换成布尔类型
        logging.info("found model:%s(table:%s)" % (name, tabelName))

        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info("found mapping: %s===>%s" % (k, v))
                mappings[k] = v
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError(
                            "Duplicate primary key for field:%s" % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError(
                "Primary key not found")
        #删除field等类变量，防止与实例变量冲突
        for k in list(attrs.keys()):
            del attrs[k]

        escaped_fields = list(map(lambda f: "%s" % f, fields))

        attrs["__mappings__"] = mappings  # 保存属性和列的映射关系
        attrs["__table__"] = tabelName
        #主键是否是自增长
        attrs["__autoIncreament__"]=autoIncreament

        attrs["__primary_key__"] = primaryKey  # 主键属性名
        attrs["__fields__"] = fields  # 除主键外的属性名

        attrs["__select__"] = "select %s,%s from %s" % (
            primaryKey, ",".join(escaped_fields), tabelName)  # select pk,field1,field2 from tablename
        attrs["__delete__"] = "delete from %s where %s=?" % (
            tabelName, primaryKey)  # delete from tablename where pk=?
        # attrs["__insert__"] = "insert into '%s' (%s,'%s') values (%s)" % (
        #     tabelName, ",".join(fields), primaryKey, create_args_string(len(fields)+1))  # insert into tablename (pk,field1,field2) values (?,?,?)#有个疑问如果插入不需要主键，主键是自动增长的呢

        attrs["__insert__"] = "insert into %s (%s,%s) values (%s)" % (
            tabelName, ",".join(fields), "" if autoIncreament else primaryKey, create_args_string(len(fields) if autoIncreament else len(fields)+1))  # insert into tablename (pk,field1,field2) values (?,?,?)#有个疑问如果插入不需要主键，主键是自动增长的呢

        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tabelName, ', '.join(map(lambda f: '`%s`=?' % (
            mappings.get(f).name or f), fields)), primaryKey)  # update tablename set field1=?,fields=? where pk=?

        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):  # 初始化时接受一个dict，用来转移为具体对象
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):  # object.key
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):  # object.key=value
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s:%s' %
                              (key, str(value)))
                setattr(self, key, value)
        return value

    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        '''
        根据条件查询表
        '''
        sql = [cls.__select__]
        if where is not None:
            sql.append("where")
            sql.append(where)

        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append("order by")
            sql.append(orderBy)

        limit = kw.get("limit", None)
        if limit:
            sql.append("limit")
            if isinstance(limit, int):
                sql.append("?")
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append("?, ?")
                args.extend(limit)
            else:
                raise ValueError("Invalid limit value: %s" % str(limit))
        rs = await select(" ".join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        '''
        根据给定的条件查找目标字段或者个数
        '''
        sql = ["select %s _num_ from %s" % (
            selectField, cls.__table__)]  # 当selectField='count(id)',则sql等于 select count(id) _num_ from table where cond=cond 返回结果保存在_num_字段中
        if where:
            sql.append("where")
            sql.append(where)
        rs = await select(" ".join(sql), args, 1)
        if rs is None or len(rs) == 0:
            return None
        return rs[0]["_num_"]

    @classmethod
    async def findByPK(cls, pk):
        '''
        根据主键找记录
        '''
        rs = await select("%s where '%s'=?" % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def save(self):
        '''
        保存实例数据到表中数据
        '''
        args = list(map(self.getValOrDefault, self.__fields__))
        autoIncreament = self.__autoIncreament__
        if not autoIncreament:#不是自动增长才需要主键
            args.append(self.getValOrDefault(self.__primary_key__))

        rs = await execute(self.__insert__, args)
        if rs != 1:
            logging.warn('failed to insert record: affected rows: %s' % rs)
        return rs

    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn(
                'failed to update by primary key: affected rows: %s' % rows)
        return rows

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warn(
                'failed to remove by primary key: affected rows: %s' % rows)
