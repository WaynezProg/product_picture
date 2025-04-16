import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# 讀取 output.csv 檔案
df = pd.read_csv("output.csv")

# 建立儲存圖片的資料夾
if not os.path.exists("url2img"):
    os.makedirs("url2img")

for idx, row in df.iterrows():
    barcode = str(row['條碼'])
    img_url = row['圖片連結']
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
                                # 取出主機名
                                from urllib.parse import urlparse
                                parsed = urlparse(img_url) # 使用原始頁面 URL 來確定主機
                                url_to_download = f"{parsed.scheme}://{parsed.netloc}{url_to_download}"

                            # 下載圖片
                            print(f"Downloading: {url_to_download}")
                            img_data = requests.get(url_to_download, timeout=10)
                            if img_data.status_code == 200:
                                with open(f"url2img/{barcode}.jpg", "wb") as f:
                                    f.write(img_data.content)
                                print(f"{barcode}.jpg 已儲存到 url2img 資料夾")
                            else:
                                print(f"{barcode} 圖片下載失敗，狀態碼: {img_data.status_code}")
                        else:
                             print(f"{barcode} 找不到可用的圖片 URL (data-src, data-thumb, or valid src)")
                    else:
                        print(f"{barcode} 在容器中找不到 img 標籤")
                else:
                    print(f"{barcode} 找不到 image--container 或 product__media 容器")
            else:
                print(f"{barcode} 訪問網頁失敗，狀態碼: {response.status_code}")
        except Exception as e:
            print(f"{barcode} 發生錯誤: {e}")
