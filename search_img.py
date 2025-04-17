from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import os
import time
from urllib.parse import quote_plus # 用於 URL 編碼

def search_and_download_google_image(query, output_filename):
    driver = None
    try:
        search_url = f"https://www.google.com/search?tbm=isch&q={quote_plus(query)}"
        print(f"搜尋 URL: {search_url}")

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0...") # 設置 User-Agent

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(search_url)

        # !!! 關鍵：等待圖片容器載入 !!!
        # 需要用開發者工具確定正確的選擇器，這裡用一個假設的 ID
        # 可能需要更複雜的等待條件或多次嘗試
        wait_selector = "#islrg" # Google 圖片結果容器的一個可能 ID (經常變化！)
        print(f"等待元素 '{wait_selector}'...")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
            )
            print("圖片容器已載入。")
            # 可以考慮再增加短暫的 time.sleep(2) 等待圖片渲染
        except Exception as e:
             print(f"等待超時或元素未找到: {e}")
             # 在這裡可能需要捲動頁面 driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
             # 然後再次嘗試等待或直接獲取 page_source

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # !!! 關鍵：找到圖片連結 !!!
        # 這部分的邏輯非常依賴 Google 當前的 HTML 結構，極易失效
        # 以下是一個非常簡化的假設，實際情況複雜得多
        image_elements = soup.select(f"{wait_selector} img") # 粗略選取圖片
        image_urls = []
        for img in image_elements:
            # 嘗試從不同屬性獲取 URL，需要大量嘗試和除錯
            src = img.get('src')
            data_src = img.get('data-src')
            # 優先選擇非 data URI 且看起來像真實連結的 URL
            if data_src and data_src.startswith('http'):
                 image_urls.append(data_src)
            elif src and src.startswith('http'):
                 image_urls.append(src)
            # 可能需要更複雜的邏輯處理 base64 data URI 或跳轉

        if not image_urls:
            print("未能在頁面源碼中找到符合條件的圖片 URL。")
            return False

        # --- 選擇策略：這裡選擇第一個找到的 URL ---
        target_url = image_urls[0]
        print(f"選擇下載 URL: {target_url}")

        # --- 下載 ---
        try:
            img_data = requests.get(target_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if img_data.status_code == 200:
                with open(output_filename, "wb") as f:
                    f.write(img_data.content)
                print(f"圖片已儲存到: {output_filename}")
                return True
            else:
                print(f"下載失敗，狀態碼: {img_data.status_code}")
                return False
        except Exception as e:
            print(f"下載過程中發生錯誤: {e}")
            return False

    except Exception as e:
        print(f"處理過程中發生錯誤: {e}")
        return False
    finally:
        if driver:
            driver.quit()

# --- 使用範例 ---
product_name = "ちいかわ ぬいぐるみ" # 範例查詢
output_file = "downloaded_image.jpg"
search_and_download_google_image(product_name, output_file)
