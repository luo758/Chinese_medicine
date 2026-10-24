"""爬取百度汉语诗词详情页。"""
import sys

import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://hanyu.baidu.com/shici/detail?pid=946d8372884d445eb0a4cc6e3826dbe8"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
SECTIONS = [
    ("poem-detail-translation", "译文"),
    ("poem-detail-zhushi", "注释"),
    ("poem-detail-shangxi", "赏析"),
    ("poem-detail-author", "作者介绍"),
]


def field_text(node):
    if not node:
        return ""
    label = node.select_one(".poem-info-gray")
    if label:
        label.extract()
    return node.get_text(strip=True)


def crawl_poem_detail():
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.find("h1").get_text(strip=True)
    author = field_text(soup.select_one("a.poem-detail-header-author"))
    dynasty = field_text(soup.select_one("span.poem-detail-header-author"))
    lines = []
    for line in soup.select(".poem-detail-main-text .line-item"):
        text = "".join(tag.get_text(strip=True) for tag in line.select(".text, .punc-item"))
        if text:
            lines.append(text)

    print(title)
    print(f"{dynasty}·{author}")
    print("\n".join(lines))
    for section_id, name in SECTIONS:
        node = soup.select_one(f"#{section_id} .poem-detail-item-content")
        if not node:
            continue
        print(f"\n【{name}】")
        text = node.get_text("\n", strip=True)
        text = "\n".join(
            line for line in text.splitlines()
            if not line.endswith(">>") and not line.startswith("来源")
        )
        print(text)


if __name__ == "__main__":
    crawl_poem_detail()
