import os
import shutil

target_dir = 'url2img'
source_dir = 'product_folder'  # 來源資料夾改為 product_folder

# 取得 product_folder 下所有子資料夾
for folder_name in os.listdir(source_dir):
    folder_path = os.path.join(source_dir, folder_name)
    if os.path.isdir(folder_path):
        # 尋找該資料夾下的所有 .jpg 檔案
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.jpg'):
                src_path = os.path.join(folder_path, filename)
                dst_path = os.path.join(target_dir, filename)
                # 複製圖片回 url2img（如已存在則覆蓋）
                shutil.copy2(src_path, dst_path)
