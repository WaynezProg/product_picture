import csv
from concurrent.futures import ThreadPoolExecutor
import requests
import os
from bs4 import BeautifulSoup

# 幫助函式：直接從指定網站下載圖片
# base_url: 網站基底，例如 "https://chiikawamarket.jp" 或 "https://nagano-market.jp"
# source_label: 來源標籤，例如 "chiikawa" 或 "nagano"
def try_direct_download(barcode, results, base_url, source_label):
    """
    嘗試從指定網站的直接路徑下載圖片：
    如果下載成功，寫入檔案並回傳 True，否則回傳 False
    """
    img_url = f"{base_url}/cdn/shop/files/{barcode}_1.jpg"
    img_response = requests.get(img_url)
    if img_response.status_code == 200:
        # 將下載到的圖片寫進檔案
        with open(f"all/{barcode}.jpg", 'wb') as f:
            f.write(img_response.content)
        print(f"{barcode} 下載成功，來源：{source_label}")
        results.append((barcode, source_label, "已儲存"))
        return True
    else:
        print(f"{barcode} 在 {source_label} 找不到圖片，狀態碼: {img_response.status_code}")
        return False

# 幫助函式：從指定網站的產品頁面下載圖片（呼叫 fetch_shortest_image_url）
# base_url: 網站基底，例如 "https://chiikawamarket.jp" 或 "https://nagano-market.jp"
# source_label: 來源標籤，例如 "chiikawa" 或 "nagano"
def try_fetch_webpage_download(barcode, results, base_url, source_label):
    """
    嘗試從指定網站的產品頁面（products/{barcode}）找尋最適合的圖片：
    成功則回傳 True，否則回傳 False
    """
    page_url = f"{base_url}/products/{barcode}"
    shortest_image_url = fetch_shortest_image_url(page_url)
    if shortest_image_url:
        img_response = requests.get(shortest_image_url)
        if img_response.status_code == 200:
            # 將下載到的圖片寫進檔案
            with open(f"all/{barcode}.jpg", 'wb') as f:
                f.write(img_response.content)
            print(f"{barcode} 下載成功，來源：{source_label} 網頁")
            results.append((barcode, source_label, "已儲存"))
            return True
        else:
            print(f"{barcode} 在 {source_label} 網頁中找不到圖片，狀態碼: {img_response.status_code}")
            return False
    else:
        print(f"{barcode} 在 {source_label} 網頁中找不到符合條件的圖片")
        return False

def fetch_shortest_image_url(page_url):
    response = requests.get(page_url)
    if "nagano" in page_url:
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            img_tags = soup.find_all('img')
            shortest_url = None
            # 假設有全域或外部可參考的 barcode 變數
            for img in img_tags:
                if 'cdn/shop/files' in img.get('src', '') and barcode in img.get('src', ''):
                    img_url = 'https:' + img['src']
                    if shortest_url is None or len(img_url) < len(shortest_url):
                        shortest_url = img_url
            return shortest_url
    elif "chiikawa" in page_url:
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_tag = soup.find('meta', {'property': 'og:image:secure_url'})
            if meta_tag:
                img_url = meta_tag['content']
                return img_url
    else:
        print(f"無法訪問頁面，狀態碼: {response.status_code}")
        return None

def download_image(barcode, results):
    # 先檢查條碼長度是否正確
    if len(barcode) != 13:
        print(f"{barcode} 無效條碼")
        results.append((barcode, "無效條碼", "未儲存"))
        return

    # 檢查圖片是否已存在
    if os.path.exists(f"all/{barcode}.jpg"):
        print(f"{barcode} 已存在")
        results.append((barcode, "已存在", "已儲存"))
        return

    # 1) 嘗試從 chiikawa 直接下載
    if try_direct_download(barcode, results, "https://chiikawamarket.jp", "chiikawa"):
        return

    # 2) 嘗試從 nagano 直接下載
    if try_direct_download(barcode, results, "https://nagano-market.jp", "nagano"):
        return

    # 3) 嘗試從 chiikawa 網頁下載
    if try_fetch_webpage_download(barcode, results, "https://chiikawamarket.jp", "chiikawa"):
        return
    else:
        # chiikawa 網頁失敗後，先標示未找到
        print(f"{barcode} 未找到圖片")
        results.append((barcode, "未找到", "未儲存"))

    # 4) 嘗試從 nagano 網頁下載
    if try_fetch_webpage_download(barcode, results, "https://nagano-market.jp", "nagano"):
        return
    else:
        print(f"{barcode} 未找到圖片")
        results.append((barcode, "未找到", "未儲存"))

# 檢查 CSV 檔案是否存在
csv_file_path = 'image_sources.csv'
existing_data = {}

if os.path.exists(csv_file_path):
    # 讀取現有的 CSV 檔案內容
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            existing_data[row['Barcode']] = row

    # 從 CSV 檔案中讀取條碼
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        barcodes = [row['Barcode'] for row in reader if row['Saved'] == '未儲存']
else:
    # 取得產品資訊
    response = requests.post("http://127.0.0.1:8668/orders/get_product_info")
    product_info = response.json()

    # 檢查 'data' 是否在 product_info 中
    if "data" in product_info:
        barcodes = [product[1].split('-')[0] for product in product_info["data"][1:]]
    else:
        print("product_info 中沒有 'data' 鍵")
        barcodes = []

results = []
if barcodes:
    # 使用多執行緒加速下載
    with ThreadPoolExecutor() as executor:
        executor.map(lambda bc: download_image(bc, results), barcodes)

    # 更新或追加新的結果
    for barcode, source, saved in results:
        existing_data[barcode] = {'Barcode': barcode, 'Source': source, 'Saved': saved}

    # 將更新後的結果寫回 CSV 檔案
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Barcode', 'Source', 'Saved']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in existing_data.values():
            writer.writerow(data)
else:
    print("沒有條碼需要處理。")