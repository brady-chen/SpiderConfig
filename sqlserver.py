# -*- coding:utf-8 -*-
# version:1.0

import pymssql

class SqlServer:
    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def GetConncet(self):
        if not self.db:
            raise (NameError, '没有设置数据库信息')
        self.conn = pymssql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db, charset='utf8')
        cur = self.conn.cursor()
        if not cur:
            raise (NameError, '连接数据库失败')
        else:
            return cur

    def ExecQuery(self, sql):
        '''
        查询操作
        :param sql: sql代码
        :return: 查询到的值(tuple)
        '''
        cur = self.GetConncet()
        cur.execute(sql)
        resList = cur.fetchall()


        #查询完毕后必须关闭连接
        self.conn.close()
        return resList

    def ExecNonQuery(self, sql):
        '''
        增删改操作
        :param sql: sql代码
        :return: None
        '''
        cur = self.GetConncet()
        cur.execute(sql)
        self.conn.commit()
        self.conn.close()

