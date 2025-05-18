import os
import shutil
from PIL import Image
from pathlib import Path

def convert_to_webp(source_dir, quality=80):
    """
    將指定目錄下的所有 JPG 圖片轉換為 WebP 格式，並保留原始圖片
    
    Args:
        source_dir (str): 源目錄路徑
        quality (int): WebP 圖片質量 (0-100)
    """
    # 確保源目錄存在
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"目錄 {source_dir} 不存在")
        return

    # 創建備份目錄
    backup_dir = source_path.parent / f"{source_path.name}_old"
    backup_dir.mkdir(exist_ok=True)

    # 計數器
    total_files = 0
    converted_files = 0
    skipped_files = 0
    error_files = []

    # 處理所有 JPG 文件
    for file_path in source_path.glob("*.jpg"):
        total_files += 1
        webp_path = source_path / f"{file_path.stem}.webp"
        backup_path = backup_dir / file_path.name
        
        try:
            # 如果備份檔案已存在，跳過
            if backup_path.exists():
                print(f"跳過 {file_path.name} - 已存在於備份目錄")
                skipped_files += 1
                continue

            # 打開圖片
            with Image.open(file_path) as img:
                # 如果圖片已經是 WebP 格式，跳過
                if img.format == "WEBP":
                    print(f"跳過 {file_path.name} - 已經是 WebP 格式")
                    skipped_files += 1
                    continue
                
                # 轉換為 WebP
                img.save(webp_path, "WEBP", quality=quality)
                print(f"已轉換: {file_path.name} -> {webp_path.name}")
                
                # 移動原始檔案到備份目錄
                shutil.move(file_path, backup_path)
                print(f"已移動原始檔案到: {backup_path}")
                
                converted_files += 1
                
                # 顯示原始和轉換後的檔案大小
                original_size = os.path.getsize(backup_path) / 1024  # KB
                new_size = os.path.getsize(webp_path) / 1024  # KB
                reduction = ((original_size - new_size) / original_size) * 100
                print(f"檔案大小: {original_size:.1f}KB -> {new_size:.1f}KB (減少 {reduction:.1f}%)")
                
        except Exception as e:
            print(f"處理 {file_path.name} 時發生錯誤: {str(e)}")
            error_files.append(file_path.name)

    # 輸出統計信息
    print(f"\n{source_dir} 目錄轉換完成:")
    print(f"總檔案數: {total_files}")
    print(f"成功轉換: {converted_files}")
    print(f"跳過檔案: {skipped_files}")
    if error_files:
        print("\n轉換失敗的檔案:")
        for file in error_files:
            print(f"- {file}")

if __name__ == "__main__":
    # 轉換 shopee 和 all 目錄下的所有圖片
    print("開始轉換 shopee 目錄...")
    convert_to_webp("ignore/shopee_old")
    print("\n開始轉換 all 目錄...")
    convert_to_webp("ignore/all_old") 