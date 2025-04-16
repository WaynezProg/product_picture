import pandas as pd
import os
import requests
from bs4 import BeautifulSoup

# 讀取 output.csv
df = pd.read_csv("output.csv", dtype=str)

# 只處理有圖片連結的條碼
df_with_url = df[df['圖片連結'].notna() & (df['圖片連結'] != '')]

# 建立儲存圖片的資料夾
if not os.path.exists("url2img"):
    os.makedirs("url2img")

# 取得 url2img 資料夾中已下載的圖片檔名（不含副檔名）
downloaded_barcodes = set()
downloaded_files = []
if os.path.exists("url2img"):
    for fname in os.listdir("url2img"):
        if fname.endswith(".jpg"):
            barcode = os.path.splitext(fname)[0]
            downloaded_barcodes.add(barcode)
            downloaded_files.append(fname)

# 印出條碼與檔名的對應關係
print("已下載圖片的條碼與檔名對應：")
for fname in downloaded_files:
    barcode = os.path.splitext(fname)[0]
    print(f"條碼: {barcode} <-> 檔名: {fname}")

# 找出有圖片連結但沒有下載到的條碼
missing_barcodes = []
for idx, row in df_with_url.iterrows():
    barcode = str(row['條碼'])
    # 處理條碼，遇到底線只取前面部分
    barcode_for_check = barcode.split("_")[0] if "_" in barcode else barcode
    if barcode_for_check not in downloaded_barcodes:
        missing_barcodes.append(barcode)

# 輸出結果，詢問是否要補齊缺少的圖片
if missing_barcodes:
    print("以下條碼有圖片連結但未下載到圖片：")
    for bc in missing_barcodes:
        print(bc)
    ans = input("是否要自動補齊這些圖片？(y/n)：").strip().lower()
    if ans == "y":
        print("開始自動補齊圖片...")
        for bc in missing_barcodes:
            img_url = df_with_url[df_with_url['條碼'] == bc]['圖片連結'].values[0]
            if pd.notna(img_url) and img_url:
                try:
                    response = requests.get(img_url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # 嘗試尋找不同的容器 class
                        container = soup.find(class_="image--container") or soup.find(class_="product__media")
                        print(container)
                        if container:
                            img_tag = container.find("img")
                            if img_tag:
                                # 決定圖片來源 URL
                                url_to_download = None
                                data_src_val = img_tag.get("data-src")
                                data_thumb_val = img_tag.get("data-thumb")
                                src_val = img_tag.get("src")

                                if data_src_val:
                                    url_to_download = data_src_val.replace("{width}x", "1200x")
                                    print(f"Using data-src: {url_to_download}")
                                elif data_thumb_val:
                                    url_to_download = data_thumb_val.replace("{width}x", "1200x")
                                    print(f"Using data-thumb: {url_to_download}")
                                elif src_val and not src_val.endswith("blank_686x.png"): # 避免使用佔位符 src
                                    url_to_download = src_val
                                    print(f"Using src: {url_to_download}")

                                if url_to_download:
                                    # 處理圖片連結（有可能是相對路徑）
                                    if url_to_download.startswith("//"):
                                        url_to_download = "https:" + url_to_download
                                    elif url_to_download.startswith("/"):
                                        from urllib.parse import urlparse
                                        parsed = urlparse(img_url)
                                        url_to_download = f"{parsed.scheme}://{parsed.netloc}{url_to_download}"

                                    # 下載圖片
                                    print(f"Downloading: {url_to_download}")
                                    img_data = requests.get(url_to_download, timeout=10)
                                    if img_data.status_code == 200:
                                        # 儲存時，檔名仍用原始條碼（含底線）
                                        with open(f"url2img/{bc}.jpg", "wb") as f:
                                            f.write(img_data.content)
                                        print(f"{bc}.jpg 已儲存到 url2img 資料夾")
                                    else:
                                        print(f"{bc} 圖片下載失敗，狀態碼: {img_data.status_code}")
                                else:
                                    print(f"{bc} 找不到可用的圖片 URL (data-src, data-thumb, or valid src)")
                            else:
                                print(f"{bc} 在容器中找不到 img 標籤")
                        else:
                            print(f"{bc} 找不到 image--container 或 product__media 容器")
                    else:
                        print(f"{bc} 訪問網頁失敗，狀態碼: {response.status_code}")
                except Exception as e:
                    print(f"{bc} 發生錯誤: {e}")
    else:
        print("已取消自動補齊圖片。")
else:
    print("所有有圖片連結的條碼都已下載到圖片。")
