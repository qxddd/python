# -*- encoding: utf-8 -*-
'''
@File    :   test.py
@Time    :   2019/05/28 17:09:22
@Author  :   qxd 
@Version :   1.0
@Contact :   1591775626@qq.com
@Desc    :   test file
'''

import http_help as hh
import json

headers = {"Referer":"http://image.fengniao.com/list_1422.html","Host":"image.fengniao.com","X-Requested-With":"XMLHttpRequest"}
start = "http://image.fengniao.com/index.php?action=getList&class_id=192&sub_classid=0&page={}&not_in_id=5356548,5356425,5356337,5356302"
res = hh.helper(headers=headers)
index = 3
url = start.format(index)
content = res.get_content("http://image.fengniao.com/slide/535/5356289_1.html",charset="gbk")
#json_connent = json.loads(content)
print(content)