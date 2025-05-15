import os
import shutil
from pathlib import Path

def copy_files():
    # 定義資料夾路徑
    change_dir = Path('change')
    all_dir = Path('shopee')
    old_version_dir = Path('old_version')

    # 確保 old_version 資料夾存在
    old_version_dir.mkdir(exist_ok=True)

    # 獲取 change 資料夾中的所有檔案
    change_files = [f.name for f in change_dir.iterdir() if f.is_file()]

    # 計數器
    success_count = 0
    not_found_count = 0
    not_found_files = []
    copy_to_all_count = 0
    copy_to_all_files = []

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
            not_found_files.append(filename)
            # 新增：將找不到的檔案從 change 複製到 shopee
            change_file_path = change_dir / filename
            shopee_file_path = all_dir / filename
            try:
                shutil.copy2(change_file_path, shopee_file_path)
                print(f'已將 {filename} 從 change 複製到 shopee')
                copy_to_all_count += 1
                copy_to_all_files.append(filename)
            except Exception as e:
                print(f'複製 {filename} 到 shopee 時發生錯誤: {str(e)}')

    # 輸出統計資訊
    print(f'\n處理完成:')
    print(f'成功複製: {success_count} 個檔案')
    print(f'找不到檔案: {not_found_count} 個')
    if not_found_files:
        print('找不到的檔案清單:')
        for nf in not_found_files:
            print(nf)
    print(f'已從 change 複製到 shopee: {copy_to_all_count} 個檔案')
    if copy_to_all_files:
        print('複製到 shopee 的檔案清單:')
        for cf in copy_to_all_files:
            print(cf)

if __name__ == '__main__':
    copy_files()
