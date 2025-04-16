import requests
from bs4 import BeautifulSoup
import pandas as pd

# 讀取 output.csv 檔案
output_df = pd.read_csv("output.csv", dtype=str)
print("output.csv 欄位：", output_df.columns)

# 篩選出圖片連結為空的條碼
no_img_df = output_df[(output_df['圖片連結'].isna()) | (output_df['圖片連結'] == '')]
barcodes = no_img_df['條碼'].tolist()
print(f"需重新查找圖片連結的條碼數量：{len(barcodes)}")

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
        print(f"嘗試網址: {url}, 來源: {source}, 條碼: {barcode}")
        try:
            r = requests.get(url, timeout=5)
            print(f"狀態碼: {r.status_code}")  # 除錯訊息
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
            print(f"例外: {e}")  # 除錯訊息
            continue
    if not found:
        results.append({
            "條碼": barcode,
            "圖片連結": "",
            "來源": "",
            "品名": ""
        })
    print(f"目前結果: {results[-1]}")  # 只印本次
    print(f"處理條碼: {barcode} 完成")

print(f"最終結果: {results}")

# 將新查到的結果合併回 output.csv
# 先將原本 output.csv 轉成 DataFrame
final_df = output_df.copy()
for res in results:
    idx = final_df[final_df['條碼'] == res['條碼']].index
    if res['圖片連結']:
        # 只更新有找到圖片連結的
        final_df.loc[idx, '圖片連結'] = res['圖片連結']
        final_df.loc[idx, '來源'] = res['來源']
        final_df.loc[idx, '品名'] = res['品名']

# 輸出結果成 CSV
final_df.to_csv("recheck_output.csv", index=False, encoding="utf-8-sig")
print(final_df)