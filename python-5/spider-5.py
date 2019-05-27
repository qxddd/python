# -*- encoding: utf-8 -*-
'''
@File    :   spider-5.py
@Time    :   2019/05/26 19:16:11
@Author  :   qxd 
@Version :   1.0
@Contact :   1591775626@qq.com
@Desc    :   get the 27270's beauty imgs
'''

import sys
sys.path.append('c:\\Users\\QXD\\Documents\\python')
import http_help as hh
import re
from threading import Thread,Lock
import time

# 获取页面URL列表
class ImageList():
    def __init__(self):
        self.__start = "https://www.2717.com/ent/meinvtupian/list_11_{}.html"
        self.__headers = {"Referer":"https://www.2717.com/ent/meinvtupian/","Host":"www.2717.com"}
        self.__res = hh.helper(headers=self.__headers)

    # 获取页面页码
    def get_page_count(self):
        content = self.__res.get_content(self.__start.format("1"),"gb2312")
        pattern = re.compile("<li><a href='list_11_(\d+).html' target='_self'>末页</a>")
        search_test = pattern.search(content)

        if search_test is not None:
            count = search_test.group(1)
            return count
        else:
            return 0

    # 获取所有页面URL的列表
    def run(self):
        page_count = int(self.get_page_count())

        if page_count == 0:
            return
        urls = [self.__start.format(i) for i in range(1,page_count)]
        return urls

urls_lock = Lock()

# 获取各个页面的详情页与图片文件URL
class Product(Thread):

    def __init__(self,urls):
        super().__init__()
        self.__urls = urls
