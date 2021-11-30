# coding=utf-8
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from pymongo import MongoClient
from pandas import json_normalize

# web交互式查询函数，
# input   查询条件keyword
# return  chrome web driver
def search(keyword):
    # 初始化chrome驱动配置
    chrome_options = webdriver.ChromeOptions()
    # 让浏览器不显示自动化测试
    chrome_options.add_argument("--lang=zh-CN")
    # 设置window系统下的chrome驱动程序
    chromedriver = webdriver.Chrome(executable_path='./driver/chromedriver.exe', options=chrome_options)

    chromedriver.get("https://patents.google.com/")
    time.sleep(3)

    # 输入查询并查找
    username_field = chromedriver.find_element_by_xpath('//*[@id="searchInput"]')
    time.sleep(5)
    username_field.send_keys(keyword)
    time.sleep(3)

    # 点击查询按钮并获取详情页
    chromedriver.find_element_by_xpath('//*[@id="searchButton"]/iron-icon').click()  # 再次点击登陆
    time.sleep(3)
    chromedriver.find_element_by_xpath('//*[@id="htmlContent"]').click()
    time.sleep(3)

    return chromedriver

def getData(chromedriver):

    # 尝试逐个获取数据
    # 专利编号
    try:
        id = chromedriver.find_element_by_xpath('//*[@id="pubnum"]').text
    except:
        id = ''

    dataList = []
    xpath = '/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[2]/section/dl[1]//dd['
    for num in range(1, 999):
        XpathRe = xpath + str(num) + ']'
        try:
            dataList.append(chromedriver.find_element_by_xpath(XpathRe).text)
        except:
            break
    try:
        if(dataList[0]=='Chinese'):
            # 公司名称
            companyName = dataList[-1]
            # 专利发明人
            Inventor = dataList[1:-1]
        else:
            companyName = ''
            Inventor = ''
    except:
        companyName = ''
        Inventor = ''

    # 专利分类
    try:
        classifications = chromedriver.find_element_by_xpath('//*[@id="target"]').text
    except:
        classifications = ''

    # 专利摘要
    try:
        abstract = chromedriver.find_element_by_xpath('//*[@id="text"]/abstract/div').text
    except:
        abstract = ''

    # 专利事件
    try:
        events = chromedriver.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/application-timeline/div').text
    except:
        events = ''

    # 专利引用
    try:
        PatentCitations = chromedriver.find_element_by_xpath('//*[@id="wrapper"]/div[3]/div[1]/div').text
    except:
        PatentCitations = ''

    # 专利被引
    try:
        CitedBy = chromedriver.find_element_by_xpath('//*[@id="wrapper"]/div[3]/div[3]/div').text
    except:
        CitedBy = ''

    # 专利要求
    try:
        claims = chromedriver.find_element_by_xpath('//*[@id="claims"]/patent-text/div').text
    except:
        claims = ''

    # 专利介绍
    try:
        Description = chromedriver.find_element_by_xpath('//*[@id="descriptionText"]/div').text
    except:
        Description = ''

    '''
    try:
        # 尝试获取数据
        classifications_cont1 = a[-1].text
        classifications_num1 = b[-1].text

        abstract1 = driver.find_element_by_xpath('//*[@id="text"]/abstract/div').text                 # 专利摘要
        PatentCitations1 = driver.find_element_by_xpath('//*[@id="wrapper"]/div[3]/div[1]/div').text  # 专利引用
        CitedBy1 = driver.find_element_by_xpath('//*[@id="wrapper"]/div[3]/div[3]/div').text          # 专利被引
        claims1 = driver.find_element_by_xpath('//*[@id="claims"]/patent-text/div').text              # 专利要求
        Description1 = driver.find_element_by_xpath('//*[@id="descriptionText"]/div').text            # 专利介绍
    except:
        abstract1 = '未找到'
        classifications_num1 = '未找到'
        classifications_cont1 = '未找到'
        PatentCitations1 = '未找到'
        CitedBy1 = '未找到'
        claims1 = '未找到'
        Description1 = '未找到'
    '''

    dataJson = {
        'id': id,
        'abstract': abstract,
        'company': companyName,
        "Inventor": Inventor,
        'events': events,
        "classifications": classifications,
        "PatentCitations": PatentCitations,
        "CitedBy": CitedBy,
        "claims": claims,
        "Description": Description
    }

    return dataJson


def saveData(oneData):
    # 连接服务器
    client = MongoClient('localhost', 27017)
    mongodb = client.patent

    # 插入数据到数据库
    tmp_df = json_normalize(oneData)
    print(tmp_df)
    query = {"id": tmp_df['id'][0]}

    # 重复检查，看是否存在数据
    count = mongodb['patent_list'].count_documents(query)
    tmp_dict = tmp_df.to_dict('records')
    # print(tmp_dict)

    if count == 0:
        # 不存在，添加
        result = mongodb['patent_list'].insert_one(tmp_dict[0])
    else:
        # 已存在，更新
        result = mongodb['patent_list'].update_one(query, {'$set': tmp_dict[0]})

    return result



if __name__ == '__main__':

    # 组成查询条件
    startDate = '20210201'
    endDate = '20210203'
    keyword = 'before:priority:' + endDate + ' ' + 'after:priority:' + startDate
    # 'before:priority:20211212 after:priority:20210101'

    # 启动chrome driver查找数据
    chromedriver = search(keyword)

    # 循环查找直至结束
    while 1:
        oneData = getData(chromedriver)
        saveData(oneData)

        # 跳转到下个专利界面
        chromedriver.find_element_by_xpath('//*[@id="nextResult"]').click()
        chromedriver.get(chromedriver.current_url)
