import pandas as pd
import requests
from bs4 import BeautifulSoup

# 讀取 output.csv ���案
df = pd.read_csv("output.csv")

# 取得網頁 title ��放到品名��位中
def fetch_title(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.text.strip()
    except Exception as e:
        print(f"Error fetching title for {url}: {e}")
    return ""

# 更新品名��位
df['品名'] = df.apply(lambda row: fetch_title(row['圖片連結']) if pd.notna(row['圖片連結']) and row['圖片連結'] else row['品名'], axis=1)

# ���出結果成 output_title.csv
df.to_csv("output_title.csv", index=False, encoding="utf-8-sig")
