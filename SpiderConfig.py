# create in 2017.07.12
# version:2.1_beta
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
from getProxies import Proxies
from sqlserver import SqlServer
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
import random
import re
# 下面这几个暂时用不到
# import sys
# import time
# import threading
# from mylog import MyLog

class SpiderConfig(object):
    # LOG_NAME = sys.argv[0][0:-3] + '.log'

    db = SqlServer(
        host='www.example.com',
        user='username',
        pwd='password',
        db='databasename'
    )

    def __init__(self, start_url):
        """
        初始化
        :type start_url: str
        :param start_url: 起始url
        :return: None
        """
        # 从txt中随机选取一条浏览器请求头部的user_agent
        def get_user_agent():
            user_agent_list = []
            f = open('user_agent.txt', 'r')
            for date_line in f:
                user_agent_list.append(date_line.replace('\n', ''))
            user_agent = random.choice(user_agent_list)
            if len(user_agent) < 10:
                user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'
                return user_agent
            else:
                return user_agent

        # 用正则表达式筛选出起始url的服务器网址
        def get_host(url):
            return re.findall(re.compile("(http)+s*://(.*?)/"), url)[0][1]

        self.start_url = start_url
        self.headers = {
            "Host": get_host(start_url),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'www.baidu.com',
            'User-Agent': get_user_agent(),
        }
        self.session = requests.session()
        self.session.headers = self.headers

    def get_urls(self, get_proxie_or_not=False):
        """
        :type get_proxie_or_not: bool
        :param get_proxie_or_not: 是否启用代理ip
        :return: 返回从起始url中获取到的目标url列表
        """
        list_url = []
        try:
            if get_proxie_or_not:
                p = Proxies()
                p.get_ip_and_port()
                self.session.proxies = {
                    "http": p.ip_and_port,
                    "https": p.ip_and_port
                }
            response = self.session.get(self.start_url, timeout=30)
            if response.status_code == 200:
                html = response.content
            else:
                # 使用selenium+phantomjs来动态获取网页
                # 更改phantomjs浏览器的头部请求
                desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
                headers = self.headers
                for key, value in headers.iteritems():
                    desired_capabilities['phantomjs.page.customHeaders.{}'.format(key)] = value
                driver = webdriver.PhantomJS(
                    desired_capabilities=desired_capabilities
                )
                driver.get(self.start_url)
                html = driver.page_source
                driver.quit()
            soup = BeautifulSoup(html, 'lxml')
            # 这里每个项目都需要重新手写BeautifulSoup文档树语法
            urls = soup.find()
            assert urls is not None
            repeat_num = 0
            for url in urls:
                if url['href'] not in list_url:
                    list_url.append(url['href'])
                else:
                    repeat_num += 1
            print "发现%d条重复链接，已清除。" % repeat_num
        except requests.ConnectTimeout:
            print "url请求超时，请检查页面是否可以访问"

        if list_url:
            return list_url
        else:
            print "目标url为空，请检查代码"
            raise ValueError

    def get_htmls(self, urls, get_proxie_or_not=False):
        """
        :type urls: list
        :type get_proxie_or_not: bool
        :param urls: 目标页面的url列表
        :param get_proxie_or_not: 是否启用代理ip
        :return: 返回目标页面的html源码
        """
        list_html = []
        for url in urls:
            try:
                if get_proxie_or_not:
                    p = Proxies()
                    p.get_ip_and_port()
                    self.session.proxies = {
                        "http": p.ip_and_port,
                        "https": p.ip_and_port
                    }
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    html = response.content
                else:
                    # 使用selenium+phantomjs来动态获取网页
                    # 更改phantomjs浏览器的头部请求
                    desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
                    headers = self.headers
                    for key, value in headers.iteritems():
                        desired_capabilities['phantomjs.page.customHeaders.{}'.format(key)] = value
                    driver = webdriver.PhantomJS(
                        desired_capabilities=desired_capabilities
                    )
                    driver.get(self.start_url)
                    html = driver.page_source
                    driver.quit()
                assert html is not None
                list_html.append(BeautifulSoup(html, 'lxml'))
            except requests.ConnectTimeout:
                print "url请求超时"
        if list_html:
            return list_html
        else:
            print "目标html列表为空，请检查代码。"
            raise ValueError

    def clean_str(self, old_str):
        """
        为了获取排版好的文章内容，所以需要手动清洗敏感内容
        由里到外第一遍清除外链，第二遍清除图片，第三遍清除<span>标签，第四遍清除<a>标签, 第五遍清楚class属性
        第六遍清除</a>，第七遍清除</span>,第八遍清除标签里的id
        :type old_str: str
        :param old_str:传入要清洗的字符串
        :return: 清洗后的字符串
        """
        assert isinstance(old_str, str)
        new_str = re.sub(re.compile(' *id="(.*?)"'), '',  # 清除标签里的id
                         re.sub(re.compile('</span>'), '',  # 清除</span>
                                re.sub(re.compile('</a>'), '',  # 清除</a>
                                       re.sub(re.compile(' *class="(.*?)"'), '',  # 清除class属性
                                              re.sub(re.compile('<a(.*?)>'), '',  # 清除<a>标签
                                                     re.sub(re.compile('<span(.*?)>'), '',  # 清除<span>标签
                                                            re.sub(re.compile('<img alt=(.*?)/>'), '',  # 清除图片
                                                                   re.sub(re.compile('a href="http:(.*?)" target="_blank">'), '', old_str))))))))  # 清除外链
        # new_str = re.sub(re.compile('责任编辑：gold'), '责任编辑：小金', new_str)
        return new_str

    def check_newest_data(self, select_sql, list_headline):
        """
        检查数据库最新的文章是否与数据源最新的数据一样
        :type select_sql: str
        :type list_headline :list
        :param select_sql: 传入获取数据库最新的文章标题的sql语句
        :param list_headline: 传入已获取到的所有文章列表
        :return: 返回更新数字，是最新则返回0，不是最新则返回要更新的次数
        """
        db = SpiderConfig.db
        # 数据源的最新标题
        newest_headline = ""
        # 示例sql代码：select_sql = "select headline from [table_name] WHERE aid=(select MAX(id) from [table_name] WHERE type='%s')" %data_name
        # 从数据库获取最新的文章标题
        if db.ExecQuery(select_sql):
            newest_headline = db.ExecQuery(select_sql)[0][0]
        else:
            newest_headline = "null"

        # 检查数据源的最新标题是否和数据库最新文章标题一致，是则返回True
        def check_update(headline):
            if newest_headline == "null" or newest_headline != headline:
                return True
            else:
                return False

        # 如果数据库最新数据与数据源最新数据不一样，则判断后添加要更新的次数
        update_num = 0
        for i in range(len(list_headline)):
            if check_update(list_headline[i]):
                update_num += 1
            else:
                break
        return update_num

