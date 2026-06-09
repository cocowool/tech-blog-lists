import json
import feedparser
import requests
from bs4 import BeautifulSoup
import time
import os


# 根据博客列表获取文章列表

# 配置信息路径
BLOGS_JSON_PATH = "tech-blog-lists-cn.json"
LATEST_POSTS_PATH = "latest_posts_cn.json"

def get_webpage_title(url):
    """如果 name 为空，尝试从网页获取 title"""
    try:
        res = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        if soup.title and soup.title.string:
            return soup.title.string.strip()
    except:
        pass
    return ""

def process_blogs():
    # 1. 读取数据
    if not os.path.exists(BLOGS_JSON_PATH):
        print(f"❌ 找不到文件: {BLOGS_JSON_PATH}")
        return

    with open(BLOGS_JSON_PATH, 'r', encoding='utf-8') as f:
        blogs = json.load(f)

    latest_posts = []
    
    print(f"🚀 开始处理 {len(blogs)} 个博客...\n")

    for i, blog in enumerate(blogs):
        name = blog.get('name', '').strip()
        url = blog.get('url', '').strip()
        rss = blog.get('rss', '').strip()
        
        print(f"[{i+1}/{len(blogs)}] 处理: {name or url}")

        # 补全空 Name
        if not name and url:
            name = get_webpage_title(url)
            blog['name'] = name
            print(f"   🔍 自动补全名称: {name}")

        # 清理无效的占位符 RSS
        if 'johndoe.com' in rss:
            rss = ""
            blog['rss'] = ""

        # 2. 检查 URL 是否存活
        is_url_alive = False
        try:
            res = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if res.status_code == 200:
                is_url_alive = True
        except:
            pass

        if not is_url_alive:
            blog['status'] = 'archived'
            print(f"   ❌ 网站无法访问，标记为 archived")
            continue

        # 3. 检查 RSS 并抓取最新文章
        if rss:
            try:
                feed = feedparser.parse(rss)
                # 判断 feed 是否有效 (至少有 1 个 entry)
                if feed.entries:
                    blog['status'] = 'active'
                    
                    # 提取最新文章
                    latest_entry = feed.entries[0]
                    title = latest_entry.get('title', '无标题')
                    link = latest_entry.get('link', url)
                    
                    # 处理发布时间
                    pub_date = "未知时间"
                    if 'published_parsed' in latest_entry and latest_entry.published_parsed:
                        pub_date = time.strftime('%Y-%m-%d', latest_entry.published_parsed)
                    elif 'updated_parsed' in latest_entry and latest_entry.updated_parsed:
                        pub_date = time.strftime('%Y-%m-%d', latest_entry.updated_parsed)
                        
                    latest_posts.append({
                        "blog_name": name,
                        "blog_url": url,
                        "title": title,
                        "link": link,
                        "pub_date": pub_date
                    })
                    print(f"   ✅ 状态: active | 最新文章: {title[:20]}...")
                else:
                    blog['status'] = 'no_rss'
                    print(f"   ⚠️ RSS 无内容，降级为 no_rss")
            except Exception as e:
                blog['status'] = 'no_rss'
                print(f"   ⚠️ RSS 解析失败，降级为 no_rss")
        else:
            blog['status'] = 'no_rss'
            print(f"   ⚠️ 无 RSS 地址，标记为 no_rss")

        time.sleep(1) # 礼貌爬取，防止被封 IP

    # 4. 保存更新后的 blogs.json
    with open(BLOGS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(blogs, f, ensure_ascii=False, indent=4)
    print(f"\n💾 已更新 {BLOGS_JSON_PATH}")

    # 5. 保存最新文章列表 latest_posts.json
    # 按发布时间倒序排列
    latest_posts.sort(key=lambda x: x['pub_date'], reverse=True)
    
    with open(LATEST_POSTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(latest_posts, f, ensure_ascii=False, indent=4)
    print(f"💾 已生成 {LATEST_POSTS_PATH}，共 {len(latest_posts)} 篇最新文章。")
    print("🎉 全部完成！请执行 hexo clean && hexo g && hexo d 部署网站。")

if __name__ == "__main__":
    process_blogs()