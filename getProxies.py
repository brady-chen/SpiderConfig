# -*- coding:utf-8 -*-
# version:2.0

from bs4 import BeautifulSoup
import time
import requests
import sys
import traceback



reload(sys)
sys.setdefaultencoding('utf8')

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           #'Connection': 'keep-alive', # 减少连接存活次数
           'Referer': 'www.baidu.com',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}


class Proxies(object):
    """
    get_data函数从代理网站抓取前两页的页面源码，并逐一判断
    :return ip_and_port
    """

    def __init__(self):
        self.start_page_num = 1
        self.end_page_num = 2
        self.START_URL = "http://www.xicidaili.com/nn/"
        self.target_urls = []
        self.list_html = []
        self.ip_and_port = ""

    def get_url_and_html(self):
        for num in range(self.start_page_num, self.end_page_num + 1):
            self.target_urls.append(self.START_URL + str(num))
        for url in self.target_urls:
            resopnse = requests.get(url, headers=headers)
            assert resopnse.status_code == 200
            soup = BeautifulSoup(resopnse.content, 'lxml')
            htmls = soup.findAll({"tr"})
            for html in htmls:
                self.list_html.append(html)

    def get_data(self):
        self.get_url_and_html()
        for html in self.list_html:
            try:
                soup = BeautifulSoup(str(html), 'lxml')
                # soup的第一列为空，需要先做次判断
                if soup.find("tr").findAll("td"):
                    ip_and_port = (
                        soup.find("tr").findAll("td")[1].get_text() +
                        ":" + soup.find("tr").findAll("td")[2].get_text()
                    )
                    proxies = {
                        "http": ip_and_port,
                        "https": ip_and_port
                    }
                    # 验证ip是否链接成功，时限2秒
                    response = requests.get(
                        "http://1212.ip138.com/ic.asp",
                        headers=headers,
                        proxies=proxies,
                        timeout=2
                    )
                    if response.status_code == 200:
                        self.ip_and_port = ip_and_port
                        print "ip和端口地址为：" + self.ip_and_port
                        print "服务器地址为:{},安全类型为:{},连接速度为:{},连接时间为:{},存活时间为:{},验证时间为:{}".format(
                            str(soup.find("tr").findAll("td")[3].get_text()).replace("\n", ""),
                            soup.find("tr").findAll("td")[4].get_text(),
                            soup.find("tr").findAll("td")[5].get_text(),
                            soup.find("tr").findAll("td")[6].find({"div", "title"}).attrs["title"],
                            soup.find("tr").findAll("td")[7].find({"div", "title"}).attrs["title"],
                            soup.find("tr").findAll("td")[8].get_text(),
                            soup.find("tr").findAll("td")[9].get_text()
                        )
                        break
                    else:
                        print "http状态码非200"
                        raise requests.ConnectionError
            except requests.ReadTimeout:
                print "此ip连接速度较慢，正在使用下一个ip"
            except requests.ConnectionError:
                print "此ip连接出错"
            except Exception as e:
                print "获取代理出错，原因为:%(errorName)s\n详细信息为:\n%(detailInfo)s" % {
                    "errorName": e, "detailInfo": traceback.format_exc()}


if __name__ == "__main__":
    p = Proxies()
    p.get_data()
    print p.ip_and_port
