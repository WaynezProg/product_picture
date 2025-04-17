import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urlparse
import time # 引入 time 模組

# Selenium 相關導入
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService # Selenium 4 更新
from webdriver_manager.chrome import ChromeDriverManager # 自動管理 ChromeDriver

print("--- Script starting ---")

# --- 設定 ---
CSV_FILE = "output.csv"
OUTPUT_FOLDER = "product_folder"
STATE_FILE = "processed_urls.txt" # <--- 恢復狀態檔案
WAIT_TIMEOUT = 10
# -------------

def download_image(url, filepath, barcode, img_num):
    """下載單張圖片"""
    try:
        img_data = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if img_data.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(img_data.content)
            print(f"  成功: {os.path.basename(filepath)}")
            return True
        else:
            print(f"  失敗: 無法下載圖片 {barcode}-{img_num} (狀態碼: {img_data.status_code}), URL: {url}")
            return False
    except Exception as e:
        print(f"  錯誤: 下載圖片 {barcode}-{img_num} 時發生錯誤: {e}, URL: {url}")
        return False

def get_full_size_url_slick_dots(thumb_url):
    """將 slick-dots 的縮圖 URL 轉換為高解析度 URL (移除 _NNNx 標記)"""
    full_url = re.sub(r'_(\d+)x\.jpg', '.jpg', thumb_url)
    return full_url

# --- 恢復讀取狀態檔案 --- 
processed_urls = set()
try:
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        processed_urls = set(line.strip() for line in f if line.strip())
    print(f"已從 '{STATE_FILE}' 載入 {len(processed_urls)} 個已處理的 URL。")
except FileNotFoundError:
    print(f"狀態檔案 '{STATE_FILE}' 不存在，將從頭開始處理。")

# --- WebDriver 初始化 ---
driver = None
try:
    print("正在初始化 WebDriver...")
    # 配置 Chrome 選項 (例如，無頭模式)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless") # 無頭模式，不在螢幕上打開瀏覽器窗口
    chrome_options.add_argument("--disable-gpu") # 某些系統需要此選項
    chrome_options.add_argument("--window-size=1920,1080") # 設定窗口大小
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36") # 設定 User-Agent

    # 使用 webdriver-manager 自動下載和管理 ChromeDriver
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("WebDriver 初始化成功。")
    except Exception as e:
        print(f"WebDriver 初始化失敗: {e}")
        print("請確保已安裝 Chrome 瀏覽器，且網路連線正常以便下載 ChromeDriver。")
        exit()

    # --- 讀取 CSV ---
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"錯誤: 找不到 CSV 檔案 '{CSV_FILE}'")
        exit()

    # 建立主輸出資料夾
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"已建立資料夾: {OUTPUT_FOLDER}")

    # --- 逐一處理每個產品 ---
    total_rows = len(df)
    skipped_count = 0 # <--- 恢復計數器
    processed_count = 0 # <--- 恢復計數器
    for idx, row in df.iterrows():
        current_row_num = idx + 1
        barcode = str(row['條碼'])
        product_url = row['圖片連結']

        if pd.isna(product_url) or not product_url:
            print(f"({current_row_num}/{total_rows}) 跳過條碼 {barcode}: 無效的產品 URL")
            continue

        # --- 結合兩種檢查方式 ---
        # 1. 檢查狀態檔案
        if product_url in processed_urls:
            # print(f"({current_row_num}/{total_rows}) 跳過條碼 {barcode}: URL 已在狀態檔案中。")
            skipped_count += 1
            continue
            
        # 2. 檢查輸出資料夾
        barcode_folder = os.path.join(OUTPUT_FOLDER, barcode)
        folder_exists = os.path.exists(barcode_folder)
        barcode_jpgs = []
        if folder_exists:
            try:
                barcode_jpgs = [f for f in os.listdir(barcode_folder) if f.lower().endswith('.jpg') and f.startswith(f'{barcode}-')]
            except OSError as e:
                print(f"警告：無法讀取資料夾 {barcode_folder} 的內容：{e}")
                pass 
        
        if len(barcode_jpgs) > 0:
            print(f"({current_row_num}/{total_rows}) 跳過條碼 {barcode}: 已有至少一張圖片。")
            skipped_count += 1
            continue
        # --- 檢查結束 ---

        print(f"\n({current_row_num}/{total_rows}) 處理條碼 {barcode} (URL: {product_url})...")

        # 建立該條碼的子資料夾 (如果需要)
        if not folder_exists:
             try:
                 os.makedirs(barcode_folder)
                 print(f"  已建立子資料夾: {barcode_folder}")
             except OSError as e:
                 print(f"錯誤：無法建立資料夾 {barcode_folder}: {e}")
                 continue

        processing_successful_for_this_url = False # <--- 恢復狀態標記
        try:
            # 使用 Selenium 訪問頁面
            print(f"  正在訪問頁面...")
            driver.get(product_url)

            # --- 等待任一縮圖容器出現 ---
            print(f"  正在等待 slick-dots 或 thumbnail-list (最多 {WAIT_TIMEOUT} 秒)... ")
            try:
                # 使用更通用的 CSS 選擇器等待任一元素
                wait_selector = "ul.slick-dots, ul.thumbnail-list"
                WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                )
                print(f"  找到縮圖容器元素。")
            except TimeoutException:
                 print(f"  警告: 在 {WAIT_TIMEOUT} 秒內找不到 <ul class='slick-dots'> 或 <ul class='thumbnail-list'> 元素")
                 processing_successful_for_this_url = True # 即使找不到也標記為已處理
                 continue # 跳到記錄狀態步驟

            # 獲取渲染後的 HTML
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')

            # --- 查找具體的縮圖列表 --- 
            thumbnail_container = soup.find('ul', class_='slick-dots')
            container_type = 'slick-dots'
            if not thumbnail_container:
                thumbnail_container = soup.find('ul', class_='thumbnail-list')
                container_type = 'thumbnail-list'

            if thumbnail_container:
                img_tags = thumbnail_container.find_all('img')
                print(f"  找到 {len(img_tags)} 張縮圖 (類型: {container_type})...")
                img_count = 1
                for img_tag in img_tags:
                    thumb_src = img_tag.get('src')
                    if thumb_src:
                        thumb_src = thumb_src.strip()
                        full_src = None
                        # --- 根據容器類型處理 URL ---
                        if container_type == 'slick-dots':
                            full_src = get_full_size_url_slick_dots(thumb_src)
                        elif container_type == 'thumbnail-list':
                            full_src = thumb_src # 直接使用 src，不移除 &width=NNN
                        else:
                            # 理論上不應到達這裡
                            print(f"警告：未知的容器類型，將直接使用 src: {thumb_src}")
                            full_src = thumb_src 
                        
                        if full_src:
                             # --- 處理 URL 前綴 --- 
                             if full_src.startswith("//"):
                                 full_src = "https:" + full_src
                             elif full_src.startswith("/"):
                                 parsed_product_url = urlparse(product_url)
                                 full_src = f"{parsed_product_url.scheme}://{parsed_product_url.netloc}{full_src}"
    
                             # --- 下載圖片 --- 
                             output_filename = f"{barcode}-{img_count}.jpg"
                             output_filepath = os.path.join(barcode_folder, output_filename)
                             print(f"  準備下載 ({container_type}): {full_src}")
                             if download_image(full_src, output_filepath, barcode, img_count):
                                 img_count += 1
                        else:
                            print("警告：無法處理縮圖 src 以獲取完整 URL")
                    else:
                        print(f"  警告: 找到一個沒有 src 的 img 標籤")
                processing_successful_for_this_url = True
            else:
                # 如果 WebDriverWait 成功但 soup.find 失敗（不太可能但以防萬一）
                print(f"  錯誤: WebDriverWait 聲稱找到容器，但在 BeautifulSoup 解析中未找到。")
                processing_successful_for_this_url = True # 仍然標記為已處理

        except TimeoutException:
            print(f"  警告: 在 {WAIT_TIMEOUT} 秒內找不到 <ul class='slick-dots'> 元素 (可能頁面結構不同或未載入)")
            processing_successful_for_this_url = True
        except WebDriverException as e:
            print(f"  錯誤: Selenium WebDriver 發生錯誤: {e}")
            pass
        except Exception as e:
            print(f"  錯誤: 處理產品頁面 {product_url} 時發生未知錯誤: {e}")
            pass

        # --- 恢復記錄狀態的邏輯 ---
        if processing_successful_for_this_url:
            try:
                with open(STATE_FILE, 'a', encoding='utf-8') as f:
                    f.write(product_url + '\n')
                processed_urls.add(product_url)
                processed_count += 1
            except Exception as e:
                print(f"  錯誤: 無法寫入狀態檔案 '{STATE_FILE}': {e}")

finally:
    # --- WebDriver 清理 ---
    if driver:
        print("\n正在關閉 WebDriver...")
        driver.quit()
        print("WebDriver 已關閉。")

    # --- 恢復統計輸出 ---
    if 'total_rows' in locals(): # 確保迴圈至少跑過一次
        print(f"\n處理統計：總計 {total_rows} 行，跳過 {skipped_count} 個已處理項，本次嘗試處理 {processed_count} 個新 URL。")

print("\n所有處理完成。") 