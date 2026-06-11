import os, sys, getopt
import re
from bs4 import BeautifulSoup
import requests
import time
import cgi
import json
import pypinyin
import chardet
from urllib.parse import urljoin


# 读取中文博客列表清单，生成 Markdown 格式的列表
def get_blog_info(url, method = "requests"):

    try:
        # config = self.read_config()
        my_cookie = ''

        my_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15'
        }

        # if config['cookie']:
        #     my_cookie = config['cookie']

        s = requests.session()
        s.keep_alive = False
        response = s.get(url, headers = my_headers, timeout = 10)
        response.raise_for_status()  # 如果响应状态码不是 200，会抛出 HTTPError 异常

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

        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取博客标题
        blog_title = soup.title.get_text(strip=True) if soup.title else ''
        
        # 获取 Description
        tag_description = soup.find('meta', attrs={'name': 'description'})
        # print(tag_description['content'])
        blog_description = tag_description['content'].strip() if tag_description and tag_description.get('content') else ''
        # print("Blog Description:" + blog_description)

        # 探测RSS
        blog_rss_url = ''
        tag_rss = soup.find('link', type=re.compile(r'application/(rss|atom)\+?xml?'))
        if tag_rss and tag_rss.get('href'):
            blog_rss_url = urljoin(url,tag_rss['href'])
        else:
            # 尝试常见路径
            common_paths = ['/feed', '/atom.xml', '/rss.xml', '/feed.xml', '/index.xml', '/?feed=rss2']
            for path in common_paths:
                try:
                    test_url = url.rstrip('/') + path
                    test_res = requests.get(test_url, headers=my_headers, timeout=5)
                    if test_res.status_code == 200:
                        content_type = test_res.headers.get('Content-Type', '')
                        text_head = test_res.text[:200].strip()
                        if 'xml' in content_type or text_head.startswith('<?xml') or '<rss' in text_head or '<feed' in text_head:
                            blog_rss_url = test_url
                            break
                except:
                    pass

        blog_data = {
            "name" : blog_title,
            "url" : url,
            "description" : blog_description,
            "rss" : blog_rss_url,
            "status" : "active" if blog_rss_url else "no_rss",
            "added_date" : time.strftime('%Y-%m-%d', time.localtime())
        }

        print("Get Blog Info Success:")
        print(json.dumps(blog_data, ensure_ascii=False, indent=4))

    except Exception as e:
        print(f"Error fetching blog info for {url}: {e}")
    # return response.text

# 持久化逻辑
# file_name = 'tech-blog-lists-cn.txt'
# fh = open(file_name, 'r', encoding='utf-8')

# markdown_text = ''

# line = fh.readline().strip()
# while line:
#     # print(line)
#     line = fh.readline().strip()
#     if line:
#         html = get_html(line)

#         html_content  = BeautifulSoup(html, 'html.parser')
#         t_title = html_content.find_all('title')[0].get_text().strip()
#         if t_title == '':
#             t_title = line

#         markdown_text += "* [" + t_title + "](" + line + ")\n"

# fh.close()

if __name__ == "__main__":
    target_url = input("Please input the target blog URL: ")
    get_blog_info(target_url)