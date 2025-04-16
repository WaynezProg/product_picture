import requests
from bs4 import BeautifulSoup
import pandas as pd

# 讀取 barcode.csv 檔案
barcode_df = pd.read_csv("barcode.csv")
print(barcode_df.columns)  # 列出所有欄位名稱
barcodes = barcode_df['條碼'].tolist()

# 網站格式
url_templates = [
    ("chiikawamarket", "https://chiikawamarket.jp/collections/chiikawahanten/products/{}"),
    ("naganomarket", "https://nagano-market.jp/collections/mochikinchaku/products/{}"),
    ("mogumogu", "https://chiikawamogumogu.shop/products/{}")
]

# 結果儲存
results = []

# 逐筆處理
for barcode in barcodes:
    # 處理條碼，遇到底線只取前面部分
    if isinstance(barcode, str) and "_" in barcode:
        barcode_for_url = barcode.split("_")[0]
    else:
        barcode_for_url = barcode
    found = False
    for source, url_format in url_templates:
        url = url_format.format(str(barcode_for_url).lower())
        print(url, source, barcode)
        try:
            r = requests.get(url, timeout=5)
            print(f"Status Code: {r.status_code}")  # 除錯訊息
            if r.status_code != 404:
                soup = BeautifulSoup(r.content, 'html.parser')
                title = soup.title.string if soup.title else "No Title"
                results.append({
                    "條碼": barcode,
                    "圖片連結": url,
                    "來源": source,
                    "品名": title
                })
                found = True
                break
        except Exception as e:
            print(f"Exception: {e}")  # 除錯訊息
            continue
    if not found:
        results.append({
            "條碼": barcode,
            "圖片連結": "",
            "來源": "",
            "品名": ""
        })
    print(f"Current Results: {results}")  # 除錯訊息
    print(f"處理條碼: {barcode} 完成")

print(f"Final Results: {results}")
# 輸出結果成 CSV 或印出來
df = pd.DataFrame(results)
df.to_csv("output.csv", index=False, encoding="utf-8-sig")
print(df)
