import os
import shutil
from pathlib import Path

def copy_files():
    # 定義資料夾路徑
    change_dir = Path('change')
    all_dir = Path('all')
    old_version_dir = Path('old_version')

    # 確保 old_version 資料夾存在
    old_version_dir.mkdir(exist_ok=True)

    # 獲取 change 資料夾中的所有檔案
    change_files = [f.name for f in change_dir.iterdir() if f.is_file()]

    # 計數器
    success_count = 0
    not_found_count = 0

    # 處理每個檔案
    for filename in change_files:
        source_path = all_dir / filename
        target_path = old_version_dir / filename

        if source_path.exists():
            try:
                shutil.copy2(source_path, target_path)
                print(f'成功複製: {filename}')
                success_count += 1
            except Exception as e:
                print(f'複製 {filename} 時發生錯誤: {str(e)}')
        else:
            print(f'在 all 資料夾中找不到檔案: {filename}')
            not_found_count += 1

    # 輸出統計資訊
    print(f'\n處理完成:')
    print(f'成功複製: {success_count} 個檔案')
    print(f'找不到檔案: {not_found_count} 個')

if __name__ == '__main__':
    copy_files()
