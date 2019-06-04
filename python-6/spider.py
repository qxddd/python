# -*- encoding: utf-8 -*-
'''
@File    :   spider.py
@Time    :   2019/05/28 19:37:35
@Author  :   qxd 
@Version :   1.0
@Contact :   1591775626@qq.com
@Desc    :   fengniaowang
'''

import sys
sys.path.append("C:/Users/QXD/Documents/python/")
import http_help as hh
import re
import threading
import json
import time
import requests

#详情页图片链接
img_list = []
index = 2

class Product(threading.Thread):

    def __init__(self):
        super().__init__()
        self._img_lock = threading.Lock()
        self._headers = {"Referer":"http://image.fengniao.com/","Host":"image.fengniao.com","X-Requested-With":"XMLHttpRequest"}
        self._start = "http://image.fengniao.com/index.php?action=getList&class_id=192&sub_classid=0&page={}&not_in_id=5356548,5356425,5356337,5356302"
        self._res = hh.helper(headers=self._headers)
        self._idx_lock = threading.Lock()

    def run(self):
        #起始页
        global index
        global img_list

        while True:
            url = self._start.format(index)
            print("开始操作{}".format(url))
            try:
                self._idx_lock.acquire()
                index += 1
                idx = index
            finally:
            
                content = self._res.get_content(url,charset="gbk")
            if content is None:
                continue
            
            

            #获取返回数据
            json_content = json.loads(content)
            #print(json_content)

            

            if json_content["status"] == 1:
                for item in json_content["data"]:
                    title = item["title"]
                    child_url = item["url"]
                    #print(child_url)

                    img_contet = self._res.get_content(child_url,charset="gbk")

                    pattern = re.compile('"pic_url_1920_b":"(.*?)\?.*"')
                    img_json = pattern.findall(img_contet)
                    #print(img_json)
                    

                    if len(img_json) > 0:
                        self._img_lock.acquire()
                        try:
                            img_list.append({"title":title,"urls":img_json})
                        finally:
                            self._img_lock.release()

                        #print(img_list)

            #time.sleep(3)

class Consumer(threading.Thread):

    def __init__(self):
        super().__init__()
        self._down_lock = threading.Lock()
        self._res = hh.helper()

    def run(self):
        global img_list

        while True:

            if len(img_list) <= 0:
                time.sleep(5)
                print("先等等")
                continue
            else:
                try:
                    self._down_lock.acquire()
                    data = img_list[0]
                    del img_list[0]
                finally:
                    self._down_lock.release()

            urls = [url.replace("\\","") for url in data["urls"]]
            
            for item_url in urls:

                try:
                    file = self._res.get_file(item_url)
                    #file = requests.get(item_url,headers={"Referer":"{}".format(item_url),"Host":"cms.qn.img-space.com"},timeout=3)
                    with open("C:\\fengniao\\{}".format(str(time.time())+".jpg"),"wb+") as f:
                        f.write(file)
                except Exception as e:
                    print(e)
                #print(item_url)
            time.sleep(2)


if __name__ == '__main__':
    p = Product()
    p.start()

    for i in range(10):
        c = Consumer()
        c.start()
