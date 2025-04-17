import os
import aiohttp
import asyncio

# ��定圖片資料��
image_dir = '/Users/waynetu/my_dev_project/product_picture/all'

async def refresh_image(session, image_name):
    # 生成 jsDelivr ��新 URL
    jsdelivr_url = f'https://purge.jsdelivr.net/gh/WaynezProg/product_picture/all/{image_name}'
    
    # 發送刷新請求
    async with session.get(jsdelivr_url) as response:
        # ���查請求結果
        if response.status == 200:
            print(f'已刷新: {jsdelivr_url}')
        else:
            print(f'刷新失敗: {jsdelivr_url}，��態碼: {response.status}')

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        # ��歷資料��中的所有圖片
        for image_name in os.listdir(image_dir):
            if image_name.endswith('.jpg'):
                tasks.append(refresh_image(session, image_name))
        await asyncio.gather(*tasks)

# ��行異步任務
asyncio.run(main())
