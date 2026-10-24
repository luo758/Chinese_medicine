"""爬取中医百科方剂列表，保存为 Excel。"""
import os
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://zhongyibaike.com/wiki/%E4%B8%AD%E5%8C%BB%E6%96%B9%E5%89%82"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "formula_list.xlsx")


def crawl_formula_list():
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    seen = set()
    rows = []
    for a in soup.select("#content a"):
        name = a.get_text(strip=True)
        href = a.get("href") or ""
        if not name or not href.startswith("/wiki/"):
            continue
        full_url = urljoin("https://zhongyibaike.com", href)
        if full_url in seen:
            continue
        seen.add(full_url)
        rows.append((name, full_url))

    wb = Workbook()
    ws = wb.active
    ws.append(["方剂名称", "链接"])
    for row in rows:
        ws.append(row)
    wb.save(OUT_FILE)
    print(f"共 {len(rows)} 条，已保存到 {OUT_FILE}")


if __name__ == "__main__":
    crawl_formula_list()
