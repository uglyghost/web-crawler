import pymysql
import pandas as pd
import os
import numpy as np

mysql_host = 'localhost'
mysql_db = 'patent'
mysql_user = 'root'
mysql_pwd = '123456'
mysql_table = 'patent_list'

# 设置参数
filePath = 'H:\\web-crawler1\\patent_data1\\'


class MYSQL:
    def __init__(self):
        # MySQL
        self.MYSQL_HOST = mysql_host
        self.MYSQL_DB = mysql_db
        self.MYSQ_USER = mysql_user
        self.MYSQL_PWD = mysql_pwd
        self.connect = pymysql.connect(
            host=self.MYSQL_HOST,
            db=self.MYSQL_DB,
            port=3306,
            user=self.MYSQ_USER,
            passwd=self.MYSQL_PWD,
            charset='utf8',
            use_unicode=False
        )
        print(self.connect)
        self.cursor = self.connect.cursor()

    def insert_mysql(self, data_json):
        """
        数据插入mysql
        :param data_json:
        :return:
        """
        sql = "insert into {}(`_id`, `title`, `assignee`, `inventor`, `priority`, `filing`, `publication`, `grant`, `result`, `representative`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(mysql_table)
        try:
            self.cursor.execute(sql, (data_json['id'], data_json['title'], data_json['assignee'], data_json['inventor/author'],
                                      data_json['priority date'], data_json['filing/creation date'], data_json['publication date'],
                                      data_json['grant date'], data_json['result link'], data_json['representative figure link']))
            self.connect.commit()
            print('数据插入成功')
        except Exception as e:
            print('e= ', e)
            print('数据插入错误')


def renameCSV(comName):
    # 获取文件夹下所有文件（其实只有一个）
    FileList = os.listdir(filePath)
    file = FileList[-1]

    oldDirPath = os.path.join(filePath, file)  # 原文件名

    # fileName = os.path.splitext(file)[0]      # 文件名
    fileType = os.path.splitext(file)[1]  # 拓展名

    newDirPath = os.path.join(filePath, comName + fileType)  # 新文件名

    os.rename(oldDirPath, newDirPath)

    return newDirPath


def main():
    mysql = MYSQL()
    comName = '专利'

    while True:

        newDirPath = renameCSV(comName)

        df = pd.read_csv(newDirPath, header=1)

        df = df.where(pd.notnull(df), None)
    # orient='records', 表示将DataFrame的数据转换成我想要的json格式
        data_json = df.to_dict(orient='records')
        for dt in data_json:
            mysql.insert_mysql(dt)

        os.remove(newDirPath)

if __name__ == '__main__':
    main()