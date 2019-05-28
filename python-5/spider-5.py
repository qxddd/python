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
import os
import requests

# 获取页面URL列表
class ImageList():
    def __init__(self):
        self.__start = "https://www.2717.com/ent/meinvtupian/list_11_{}.html"
        self.__headers = {"Referer":"https://www.2717.com/ent/meinvtupian/","Host":"www.2717.com"}
        self.__res = hh.helper(headers=self.__headers)

    # 获取页面页码
    def get_page_count(self):
        content = self.__res.get_content(self.__start.format("1"),"gb2312")
        pattern = re.compile("<li><a href='list_11_(\d+?).html' target='_self'>末页</a>")
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

urls_lock = Lock()          # 图片列表页的列表锁
imgs_lock = Lock()          # 图片详情页列表的锁
imgs_start_urls = []        # 初始化一个存放所有图片详情页的列表

# 获取各个页面的详情页与图片文件URL
class Product(Thread):

    def __init__(self,urls):
        super().__init__()
        self.__urls = urls
        self.__headers = {"Referer":"https://www.2717.com/ent/meinvtupian/","Host":"www.2717.com"}

        self.__res = hh.helper(headers=self.__headers)

    # 将抓取失败的URL重新放回队列中
    def add_fail_url(self,url):
        print("{}该URL抓取失败".format(url))
        global urls_lock
        if urls_lock.acquire():
            self.__urls.insert(0,url)
            urls_lock.release()

    # 匹配图片详情页地址
    def get_page_list(self,content):
        pattern = re.compile('<li> <a href="(.*?)" title="(.*?)" class="MMPic" target="_blank">')
        list_page = re.findall(pattern,content)
        
        return list_page

    # 获取图片详情页图片地址列表
    def run(self):
        print("#"*40)
        while True:
            global urls_lock,imgs_start_urls
            if len(self.__urls) > 0:
                if urls_lock.acquire():             # 获得详情页URL列表的锁
                    last_url = self.__urls.pop()    # 弹出左后一个并删除
                    urls_lock.release()             # 释放锁
                print("正在操作{}".format(self.__urls))

                content = self.__res.get_content(last_url,"gb2312")
                if content is not None:
                    html = self.get_page_list(content)  # 获取图片详情页地址

                    if len(html) == 0:
                        self.add_fail_url(last_url)
                    else:
                        if imgs_lock.acquire():
                            imgs_start_urls.extend(html)    # 将获取到的图片详情页URL添加到列表
                            imgs_lock.release()

                    time.sleep(5)
                else:
                    print("所有链接已经处理完毕")
            
            else:
                print("所有链接已经运行完成")
                break

class Consumer(Thread):

    def __init__(self):
        super().__init__()
        #self.__urls = urls
        self.__headers = {"Referer":"https://www.2717.com/ent/meinvtupian/","Host":"www.2717.com"}

        self.__res = hh.helper(headers=self.__headers)

    # 图片下载方法
    def download_img(self,filder,img_down_url,filename):
        file_path = "f:\\beautyhome\\{}".format(filder)
        
        # 判断目录是否存在，不存在就创建
        if not os.path.exists(file_path):
            os.mkdir(file_path)

        if os.path.exists("f:\\beautyhome\\{}\\{}".format(filder,filename)):
            return
        
        else:
            try:
                img = requests.get(img_down_url,headers={"Host":"t1.hddhhn.com"},timeout=3)
            except Exception as e:
                print(e)
            
            print("{}写入图片".format(img_down_url))

            try:
                with open("f:\\beautyhome\\{}\\{}".format(filder,filename),"wb+") as f:
                    f.write(img.content)
            except Exception as e:
                print(e)
                return

    # 获取图片链接并下载
    def run(self):

        while True:
            global imgs_start_urls,imgs_lock

            if len(imgs_start_urls) > 0:
                if imgs_lock.acquire():
                    img_url = imgs_start_urls[0]        # 获取图片详情页链接列表的第一个
                    del imgs_start_urls[0]              # 取到第一个链接之后删除
                    imgs_lock.release()
            else:
                continue

            img_url = img_url[0]
            start_index = 1
            base_url = img_url[0:img_url.rindex(".")]    # 获取详情页的地址

            while True:

                img_url = "https://www.2717.com/{}_{}.html".format(base_url,start_index)   # 拼接为完整的URL
                content = self.__res.get_content(img_url,charset="gbk")

                if content is not None:
                    pattern = re.compile('<div class="articleV4Body" id="picBody">[\s\S]*?img alt="(.*?)" src="(.*?)" />')
                    img_down_url = pattern.search(content)        # 获取到了图片地址

                    if img_down_url is not None:
                        filder = img_down_url.group(1)
                        img_down_url = img_down_url.group(2)
                        filename = img_down_url[img_down_url.rindex("/")+1:]
                        self.download_img(filder,img_down_url,filename)     # 下载图片

                    else:
                        print("-"*40)
                        print(content)
                        break
                
                else:
                    print("{}链接加载失败".format(img_url))

                    if imgs_lock.acquire():
                        imgs_start_urls.append(img_url)
                        imgs_lock.release()
                
                start_index += 1

if __name__ == '__main__':

    img = ImageList()
    urls = img.run()
    for i in range(1,2):
        p = Product(urls)
        p.start()
    for i in range(1,2):
        c = Consumer()
        c.start()

