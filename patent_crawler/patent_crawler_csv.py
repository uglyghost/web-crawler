# coding=utf-8
import os
from selenium import webdriver
import time
from pymongo import MongoClient
import csv
import datetime
import re
from ws_datetime import Date
from bson import ObjectId
import random

# 设置参数
filePath = 'H:\\web-crawler1\\patent_data\\'

# 连接服务器
user = 'wenshu'
pwd = '123456'
host = '10.220.139.141'
port = '27017'
db_name = 'wenshu'

uri = "mongodb://%s:%s@%s" % (user, pwd, host + ":" + port + "/" + db_name)

# 连接数据库

client = MongoClient(uri)
# client = MongoClient('localhost', 27017)
mongodb = client.patent


def first_word(text: str) -> str:
    return re.search("([\w']+)", text).group(1)

# 初始化chrome驱动配置
chrome_options = webdriver.ChromeOptions()
# 让浏览器不显示自动化测试
chrome_options.add_argument("-–lang=zh-CN")
# chrome_options.add_argument("--headless")
prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': filePath}
chrome_options.add_experimental_option('prefs', prefs)
# 设置window系统下的chrome驱动程序
chromedriver = webdriver.Chrome(executable_path='./driver/chromedriver.exe', options=chrome_options)
cookies = {'value': '=205=QrIgq6taS0vVrGF-ip1jLrhJFtGyfFNF4kZxSNv7yLb78aIQz2_oslAhUcBePAuL1L1tt5Zuab6DlE580VgTsWMkHvukLJ_2fHaNeI98W9TgB8ZvbUcyJ7DcD8s3QShYqwwtFHHFhWRi-jMtU8azklbXunUwVimHAlWHS6r-x7ISmGehd_fbzxYoh0ZY7mWPRyiTDzCLoEKv44ZsUOjp5yh5DxBpsMqeM94Bek23St7uLrGO58vZyibfT1vkRu3fBI1Cu84Oj7uszw',
           'name': 'NID'}


# web交互式查询函数，
# input   查询条件keyword
# return  chrome web driver
def search(url):

    flag = False  # 是否找到专利 1: 找到  0: 未找到

    try:
        chromedriver.get(url=url)
        chromedriver.add_cookie(cookie_dict=cookies)
        time.sleep(3)

        try:
            number = chromedriver.find_element_by_xpath('/html/body/search-app/search-results/search-ui/div/div/div['
                                               '2]/div/div/div[1]/div[2]/div[1]/span[1]/span[3]').text
            print(number)
        except:
            print("未找到任何专利")
            #chromedriver.close()
            return flag

        chromedriver.find_element_by_xpath('//*[@id="count"]/div[1]/span[2]/a').click()
        time.sleep(random.randint(55, 65))
        dl_wait = True
        while dl_wait:
            time.sleep(random.randint(1, 3))
            for fname in os.listdir(filePath):
                if fname.endswith('.csv') or fname.endswith('.crdownload'):
                    dl_wait = False

        flag = True
        #chromedriver.close()
    except:
        #chromedriver.close()
        flag = False

    return flag


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


def saveData(newDirPath):
    collection = mongodb['patent_list']

    # print('开始数据存储：{0}'.format(datetime.datetime.now()))
    patentNum = 0
    with open(newDirPath, 'r', encoding="utf-8") as csvfile:
        next(csvfile)
        reader = csv.reader(csvfile)
        keys = []
        oneData = {}
        for i, row in enumerate(reader):
            if i == 0:
                for key in row:
                    keys.append(first_word(key))
                # print(keys)
            else:
                for index, value in enumerate(row):
                    # print(keys[index])
                    oneData[keys[index]] = value
                query = {'id': oneData['id']}
                existing_document = collection.find_one(query)
                if not existing_document:
                    collection.insert_one(oneData)
                else:
                    collection.update_one(oneData, {'$set': query})
                oneData = {}
                patentNum += 1

    os.remove(newDirPath)  # 删除原文件

    # print('结束数据存储：{0}'.format(datetime.datetime.now()))

    return patentNum


def next_month(dateTime):

    start = Date.str_to_date(dateTime)
    next = start + datetime.timedelta(days=-2)

    return next.strftime('%Y%m%d')

if __name__ == '__main__':
    # 组成查询条件
    '''
    collection = mongodb['name_list']
    tmp = mongodb['tmp']

    query = {'_id': ObjectId('61a8ca8a763ff85ad5a4ca4f')}
    index = tmp.find_one(query)
    processNum = index['num']

    allcompany = collection.find().skip(index['num'])
    '''
    comName = '专利'

    endData = '20220214'

    startData = next_month(endData)

    while 1:
        url = 'https://patents.google.com/?before=priority:' + endData + '&after=priority:' + startData + '&language=CHINESE&type=PATENT'

        # 查找到制定网页
        # Flag = search(url)
        Flag = True

        if Flag:
            newDirPath = renameCSV(comName)

            patentNum = saveData(newDirPath)
        else:
            patentNum = 0

        print('{0}找到{1}个专利'.format(startData, patentNum))

        endData = startData
        startData = next_month(startData)
