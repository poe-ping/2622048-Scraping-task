import csv
import os
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

start_url = "https://www.musashino-u.ac.jp/"
target_domain = urlparse(start_url).netloc

sitemap_dict = {}  
visited = set()  
queue = [start_url]  

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

MAX_PAGES = 30  

print("=== サイトマップ抽出処理を開始します ===")

while queue and len(sitemap_dict) < MAX_PAGES:
    current_url = queue.pop(0).split("#")[0]

    if not current_url or current_url in visited:
        continue

    visited.add(current_url)

    if urlparse(current_url).netloc != target_domain:
        continue

    if current_url.lower().endswith(
        (".pdf", ".jpg", ".png", ".gif", ".zip", ".css", ".js")
    ):
        continue

    print(f"[{len(sitemap_dict) + 1}件目] 取得中: {current_url}")

    try:
        time.sleep(1)

        res = requests.get(current_url, headers=headers, timeout=10)

        if (
            res.status_code != 200
            or "text/html" not in res.headers.get("Content-Type", "")
        ):
            continue

        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.content, "html.parser")

        title_tag = soup.find("title")
        title_text = (
            title_tag.get_text(strip=True)
            if title_tag
            else "タイトルなし"
        )
        sitemap_dict[current_url] = title_text

        for a in soup.find_all("a", href=True):
            full_url = urljoin(current_url, a["href"]).split("#")[0]
            if (
                urlparse(full_url).netloc == target_domain
                and full_url not in visited
                and full_url not in queue
            ):
                queue.append(full_url)

    except Exception as e:
        print(f"エラー発生 ({current_url}): {e}")
        continue

script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
csv_file = os.path.join(script_dir, "musashino_sitemap.csv")

with open(csv_file, mode="w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["URL", "Title"])
    for url, title in sitemap_dict.items():
        writer.writerow([url, title])

print(
    f"\n=== 完了: 合計 {len(sitemap_dict)} ページのURLとタイトルを {csv_file} に保存しました ==="
)