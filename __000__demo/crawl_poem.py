"""爬取百度汉语古诗词列表。页面由前端渲染，列表数据来自搜索接口。"""
import json
import sys

import requests

sys.stdout.reconfigure(encoding="utf-8")

API = "https://hanyu.baidu.com/edu-web-go/hanyu/search"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://hanyu.baidu.com/hanyu-page/poem/list",
}
SEARCH_PARAM = {
    "word": "古诗词",
    "searchCondition": {
        "mustRecite": 0,
        "version": [],
        "grade": [],
        "gradeStage": [],
        "author": [],
        "theme": [],
        "dynasty": [],
    },
}


def fetch_page(pn):
    params = {
        "query": "古诗词",
        "smpid": "",
        "searchParam": json.dumps(SEARCH_PARAM, ensure_ascii=False, separators=(",", ":")),
        "pn": pn,
        "srcid": "51369",
        "extParams": "{}",
        "isBaikanMCP": 0,
        "flag": 0,
    }
    resp = requests.get(API, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    if data.get("errno") != 0:
        raise RuntimeError(data.get("errmsg"))
    return data["data"]


def crawl_poems():
    pn = 1
    total = 0
    while True:
        page = fetch_page(pn)
        for item in page.get("dataList") or []:
            total += 1
            name = (item.get("nameInfo") or {}).get("name", "")
            author = (item.get("authorInfo") or {}).get("author", "")
            dynasty = (item.get("authorInfo") or {}).get("dynasty", "")
            print(f"{total}. {name}  {dynasty}·{author}")
            print(f"   {item.get('url', '')}")
        if not page.get("hasMore"):
            break
        pn += 1
    print(f"共 {total} 首")


if __name__ == "__main__":
    crawl_poems()
