import csv
from concurrent.futures import ThreadPoolExecutor
import requests
import os
from bs4 import BeautifulSoup
def fetch_shortest_image_url(page_url):
    response = requests.get(page_url)
    if "nagano" in page_url:
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            img_tags = soup.find_all('img')
            shortest_url = None
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
    if len(barcode) != 13:
        print(f"{barcode} 無效條碼")
        results.append((barcode, "無效條碼", "未儲存"))
        return

    if os.path.exists(f"all/{barcode}.jpg"):
        print(f"{barcode} 已存在")
        results.append((barcode, "已存在", "已儲存"))
        return

    img_url = f"https://chiikawamarket.jp/cdn/shop/files/{barcode}_1.jpg"
    img_response = requests.get(img_url)
    if img_response.status_code == 200:
        with open(f"all/{barcode}.jpg", 'wb') as f:
            f.write(img_response.content)
        print(f"{barcode} 下載成功，來源：chiikawa")
        results.append((barcode, "chiikawa", "已儲存"))
        return
    else:
        print(f"{barcode} 在 chiikawa 找不到圖片，狀態碼: {img_response.status_code}")

    img_url = f"https://nagano-market.jp/cdn/shop/files/{barcode}_1.jpg"
    img_response = requests.get(img_url)
    if img_response.status_code == 200:
        with open(f"all/{barcode}.jpg", 'wb') as f:
            f.write(img_response.content)
        print(f"{barcode} 下載成功，來源：nagano")
        results.append((barcode, "nagano", "已儲存"))
        return
    else:
        print(f"{barcode} 在 nagano 找不到圖片，狀態碼: {img_response.status_code}")

    page_url = f"https://chiikawamarket.jp/products/{barcode}"
    shortest_image_url = fetch_shortest_image_url(page_url)
    if shortest_image_url:
        img_response = requests.get(shortest_image_url)
        if img_response.status_code == 200:
            with open(f"all/{barcode}.jpg", 'wb') as f:
                f.write(img_response.content)
            print(f"{barcode} 下載成功，來源：chiikawa 網頁")
            results.append((barcode, "chiikawa", "已儲存"))
            return
        else:
            print(f"{barcode} 在 chiikawa 網頁中找不到圖片，狀態碼: {img_response.status_code}")
    else:
        print(f"{barcode} 在 chiikawa 網頁中找不到符合條件的 img 標籤")

    print(f"{barcode} 未找到圖片")
    results.append((barcode, "未找到", "未儲存"))
    
    page_url = f"https://nagano-market.jp/products/{barcode}"
    shortest_image_url = fetch_shortest_image_url(page_url)
    if shortest_image_url:
        img_response = requests.get(shortest_image_url)
        if img_response.status_code == 200:
            with open(f"all/{barcode}.jpg", 'wb') as f:
                f.write(img_response.content)
            print(f"{barcode} 下載成功，來源：nagano 網頁")
            results.append((barcode, "nagano", "已儲存"))
            return
        else:
            print(f"{barcode} 在 nagano 網頁中找不到圖片，狀態碼: {img_response.status_code}")
    else:
        print(f"{barcode} 在 nagano 網頁中找不到符合條件的圖片")

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
    with ThreadPoolExecutor() as executor:
        executor.map(lambda barcode: download_image(barcode, results), barcodes)

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