import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin

base_url = "https://www.parade-inc.net/?s=+%E3%81%A1%E3%81%84%E3%81%8B%E3%82%8F"
search_url = f"{base_url}/?s=ちいかわ"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def get_all_search_pages(start_url):
    pages = [start_url]
    while True:
        res = requests.get(pages[-1], headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        next_page = soup.select_one('a.next.page-numbers')
        if next_page:
            next_url = next_page['href']
            pages.append(next_url)
        else:
            break
    return pages

def get_product_links(search_page_url):
    res = requests.get(search_page_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    product_links = [a['href'] for a in soup.select('a.item')]
    return product_links

def download_product_images(product_url, folder="parade_images"):
    res = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.select_one("h1.entry-title").text.strip()
    safe_title = sanitize_filename(title)

    img_tags = soup.select('div.woocommerce-product-gallery img, div.entry-content img')
    img_urls = {img['src'] for img in img_tags if 'src' in img.attrs}

    if not os.path.exists(folder):
        os.makedirs(folder)

    for i, img_url in enumerate(img_urls):
        try:
            img_res = requests.get(img_url, headers=headers)
            if img_res.status_code == 200:
                ext = os.path.splitext(img_url)[1].split('?')[0]
                filename = f"{safe_title}_{i+1}{ext}"
                with open(os.path.join(folder, filename), 'wb') as f:
                    f.write(img_res.content)
                print(f"✅ 下載圖片：{filename}")
        except Exception as e:
            print(f"❌ 錯誤：{img_url} - {e}")

# 主流程
search_pages = get_all_search_pages(search_url)
all_products = []
for page in search_pages:
    all_products.extend(get_product_links(page))

print(f"共找到 {len(all_products)} 筆商品，開始下載圖片...")

for product_url in all_products:
    download_product_images(product_url)
