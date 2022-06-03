import os, sys, getopt
import re
from bs4 import BeautifulSoup
import requests
import time
import cgi
import json
import pypinyin
import chardet

# 读取中文博客列表清单，生成 Markdown 格式的列表
def get_html(url, method = "requests"):
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

    # 判断网页编码
    charset_data = chardet.detect( response.content )
    if charset_data['encoding'].lower() != response.encoding.lower():
        if charset_data['confidence'] > 0.9:
            # Reference : https://blog.csdn.net/weixin_45975639/article/details/123737275
            response.encoding = charset_data['encoding']
        else:
            charset = re.search(r'charset=["|\'](.*?)["|\']', response.text ).group(1).strip()
            # print(charset)
            if charset:
                response.encoding = charset


    return response.text

file_name = 'tech-blog-lists-cn.txt'
fh = open(file_name, 'r', encoding='utf-8')

markdown_text = ''

line = fh.readline().strip()
while line:
    # print(line)
    line = fh.readline().strip()
    if line:
        html = get_html(line)

        html_content  = BeautifulSoup(html, 'html.parser')
        t_title = html_content.find_all('title')[0].get_text().strip()
        if t_title == '':
            t_title = line

        markdown_text += "* [" + t_title + "](" + line + ")\n"

fh.close()

print(markdown_text)