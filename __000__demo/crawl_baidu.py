"""爬取百度首页：标题和导航链接。"""
import sys

import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://www.baidu.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def crawl_baidu():
    resp = requests.get(URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    resp.encoding = "utf-8"

    # print(resp.text)

    # 把网站内容结构化处理
    soup = BeautifulSoup(resp.text, "html.parser")
    # 获取标题
    title = soup.title.get_text(strip=True) if soup.title else ""
    print(f"状态码: {resp.status_code}")
    print(f"标题: {title}")
    print("导航链接:")
    for a in soup.select("a"):
        text = a.get_text(strip=True)
        href = a.get("href")
        if text and href:
            print(f"- {text}: {href}")


if __name__ == "__main__":
    crawl_baidu()
