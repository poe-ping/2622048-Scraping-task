import csv
import os
import time
from collections import deque
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

start_url = "https://www.musashino-u.ac.jp/"
target_domain = urlparse(start_url).netloc

MAX_PAGES = 5000 

sitemap_dict = {}  
visited = set()  
queue = deque([start_url])  
queued_urls = {start_url} 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
csv_file = os.path.join(script_dir, "musashino_sitemap.csv")


with open(csv_file, mode="w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["URL", "Title"])

print("=== サイトマップ抽出処理を開始します ===")

session = requests.Session()
session.headers.update(headers)

try:
    while queue and len(sitemap_dict) < MAX_PAGES:
        current_url = queue.popleft().split("#")[0]

        if not current_url or current_url in visited:
            continue

        visited.add(current_url)

        if urlparse(current_url).netloc != target_domain:
            continue

        if current_url.lower().endswith(
            (".pdf", ".jpg", ".png", ".gif", ".zip", ".css", ".js", ".mp4", ".xlsx", ".docx")
        ):
            continue

        print(f"[{len(sitemap_dict) + 1}/{MAX_PAGES}] 取得中: {current_url}")

        try:
           
            time.sleep(0.3)

            res = session.get(current_url, timeout=10)

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

            # Append immediately to CSV so progress isn't lost if interrupted
            with open(csv_file, mode="a", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([current_url, title_text])

            for a in soup.find_all("a", href=True):
                full_url = urljoin(current_url, a["href"]).split("#")[0]
                if (
                    urlparse(full_url).netloc == target_domain
                    and full_url not in visited
                    and full_url not in queued_urls
                ):
                    queue.append(full_url)
                    queued_urls.add(full_url)

        except Exception as e:
            print(f"エラー発生 ({current_url}): {e}")
            continue

except KeyboardInterrupt:
    print("\n処理が手動で中断されました。これまでのデータは保存されています。")

print(
    f"\n=== 完了: 合計 {len(sitemap_dict)} ページのURLとタイトルを {csv_file} に保存しました ==="
)