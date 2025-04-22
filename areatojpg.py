import os
from PIL import Image

def convert_images_to_jpg(src_folder, dst_folder):
    for root, dirs, files in os.walk(src_folder):
        # 計算對應的目標資料夾路徑
        rel_path = os.path.relpath(root, src_folder)
        target_root = os.path.join(dst_folder, rel_path)
        if not os.path.exists(target_root):
            os.makedirs(target_root)
        for file in files:
            file_lower = file.lower()
            if file_lower.endswith(('.png', '.jpeg', '.jpg', '.bmp', '.webp', '.tiff', '.gif')):
                file_path = os.path.join(root, file)
                # 產生新的jpg檔名
                base_name = os.path.splitext(file)[0]
                new_file_path = os.path.join(target_root, base_name + '.jpg')
                # 如果已經是jpg且目標檔案已存在就略過
                if file_lower.endswith('.jpg') and os.path.abspath(file_path) == os.path.abspath(new_file_path):
                    continue
                try:
                    with Image.open(file_path) as im:
                        # 轉成RGB避免透明通道問題
                        rgb_im = im.convert('RGB')
                        rgb_im.save(new_file_path, 'JPEG')
                    print(f"已轉換: {file_path} -> {new_file_path}")
                except Exception as e:
                    print(f"轉換失敗: {file_path}, 錯誤: {e}")

if __name__ == "__main__":
    area_folder = 'area'
    area_jpg_folder = 'area_jpg'
    convert_images_to_jpg(area_folder, area_jpg_folder)
