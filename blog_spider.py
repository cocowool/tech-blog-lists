import os, sys, getopt
import re
from bs4 import BeautifulSoup
import requests
import time
import cgi
import json
import pypinyin

# 读取中文博客列表清单，生成 Markdown 格式的列表
def get_html(self, url, method = "requests"):
    # config = self.read_config()
    my_cookie = ''

    my_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15'
    }

    # if config['cookie']:
    #     my_cookie = config['cookie']

    s = requests.session()
    s.keep_alive = False
    response = s.get(url, headers = my_headers, cookies = my_cookie)
    response.encoding = 'utf-8'

    return response.text

file_name = 'tech-blog-lists-cn.txt'
fh = open(file_name, 'r', encoding='utf-8')

line = fh.readline().strip()
while line:
    print(line)
    line = fh.readline().strip()
    # html = get_html(line)

fh.close()