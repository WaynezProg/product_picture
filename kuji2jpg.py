import os
import shutil
from PIL import Image

def convert_kuji_png_to_jpg(src_folder, dst_folder, all_jpg_folder):
    # 確保目標資料夾存在
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    if not os.path.exists(all_jpg_folder):
        os.makedirs(all_jpg_folder)

    for root, dirs, files in os.walk(src_folder):
        # 計算相對於src_folder的路徑
        rel_path = os.path.relpath(root, src_folder)
        # 目標資料夾為dst_folder/rel_path
        target_root = os.path.join(dst_folder, rel_path) if rel_path != '.' else dst_folder
        if not os.path.exists(target_root):
            os.makedirs(target_root)
        for file in files:
            file_lower = file.lower()
            if file_lower.endswith('.png'):
                file_path = os.path.join(root, file)
                # 保持原始檔名，只改副檔名為.jpg
                base_name = os.path.splitext(file)[0]
                new_file_path = os.path.join(target_root, base_name + '.jpg')
                all_jpg_path = os.path.join(all_jpg_folder, base_name + '.jpg')
                # 如果已經轉換過就跳過
                if os.path.exists(new_file_path):
                    print(f"已存在，略過: {new_file_path}")
                else:
                    try:
                        with Image.open(file_path) as im:
                            rgb_im = im.convert('RGB')
                            rgb_im.save(new_file_path, 'JPEG')
                        print(f"已轉換: {file_path} -> {new_file_path}")
                    except Exception as e:
                        print(f"轉換失敗: {file_path}, 錯誤: {e}")
                # 不論是新轉換還是已存在，都要複製到all_jpg_folder（如有同名會覆蓋）
                try:
                    shutil.copy2(new_file_path, all_jpg_path)
                    print(f"已複製到: {all_jpg_path}")
                except Exception as e:
                    print(f"複製失敗: {new_file_path} -> {all_jpg_path}, 錯誤: {e}")

if __name__ == "__main__":
    kuji_folder = 'kuji'
    kuji_jpg_folder = 'kuji_jpg'
    kuji_all_folder = 'kuji_all'
    convert_kuji_png_to_jpg(kuji_folder, kuji_jpg_folder, kuji_all_folder)
