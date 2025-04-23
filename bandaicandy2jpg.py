import os
from PIL import Image

# 新增：設定最大處理圖片數量（測試用）
MAX_IMAGES = 20  # 若要全跑請設為 None

def convert_images_to_jpg_and_collect_all(src_folder, all_folder):
    if not os.path.exists(all_folder):
        os.makedirs(all_folder)

    # 收集所有圖片檔案路徑
    image_files = []
    for root, dirs, files in os.walk(src_folder):
        if os.path.abspath(root) == os.path.abspath(all_folder):
            continue
        for file in files:
            if file.lower().endswith(('.png', '.jpeg', '.jpg', '.bmp', '.gif', '.webp', '.tiff')):
                file_path = os.path.join(root, file)
                image_files.append((root, file, file_path))

    total_images = len(image_files)
    print(f"共找到 {total_images} 張圖片檔案。")
    if MAX_IMAGES is not None:
        print(f"僅處理前 {MAX_IMAGES} 張圖片（測試用）...")
        image_files = image_files[:MAX_IMAGES]

    for idx, (root, file, file_path) in enumerate(image_files, 1):
        try:
            with Image.open(file_path) as img:
                rgb_img = img.convert('RGB')
                # 只保留原始檔名（副檔名改為 .jpg）
                base_name = os.path.splitext(file)[0]
                jpg_name = f"{base_name}.jpg"
                save_path = os.path.join(all_folder, jpg_name)
                rgb_img.save(save_path, 'JPEG')
                print(f"[{idx}/{len(image_files)}] 已轉換: {file_path} → {save_path}")
        except Exception as e:
            print(f"[{idx}/{len(image_files)}] 無法處理檔案 {file_path}: {e}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bandai_candy_folder = os.path.join(current_dir, 'bandai_candy')
    all_folder = os.path.join(bandai_candy_folder, 'all')
    convert_images_to_jpg_and_collect_all(bandai_candy_folder, all_folder)
