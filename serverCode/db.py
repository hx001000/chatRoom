from pymysql import connect
from serverCode.config import *


class DB(object):

    def __init__(self):
        # 连接到数据库
        self.dbConnect = connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            charset='utf8'
        )

        # 获取游标
        self.cursor = self.dbConnect.cursor()

    def queryFromDb(self, sql):
        '''执行SQL查询'''
        # 执行SQL语句
        self.cursor.execute(sql)
        # 获取查询结果
        queryResult = self.cursor.fetchone()
        # 判断是否有结果
        if not queryResult:
            return None
        # 获取字段
        fileds = [filed[0] for filed in self.cursor.description]
        # 使用字段和结果数据合成字典 以供返回使用
        returnData = {}
        for filed, value in zip(fileds, queryResult):
            returnData[filed] = value

        return returnData

    def close(self):
        '''释放数据库资源'''
        self.cursor.close()
        self.dbConnect.close()

if __name__ == '__main__':
    db = DB()
    data = db.queryFromDb("select * from users where user_name='user1'")
    print(data)
    db.close()