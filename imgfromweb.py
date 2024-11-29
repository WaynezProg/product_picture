import requests
from bs4 import BeautifulSoup

def fetch_shortest_image_url(page_url):
    response = requests.get(page_url)
    if "nagano" in page_url:
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            img_tags = soup.find_all('img')
            shortest_url = None
            for img in img_tags:
                if 'cdn/shop/files' in img.get('src', '') and barcode in img.get('src', ''):
                    img_url = 'https:' + img['src']
                    if shortest_url is None or len(img_url) < len(shortest_url):
                        shortest_url = img_url
            return shortest_url
    elif "chiikawa" in page_url:
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_tag = soup.find('meta', {'property': 'og:image:secure_url'})
            if meta_tag:
                img_url = meta_tag['content']
                return img_url
    else:
        print(f"無法訪問頁面，狀態碼: {response.status_code}")
        return None


barcode = "4582662949553"
page_url = f"https://nagano-market.jp/products/{barcode}"
shortest_image_url = fetch_shortest_image_url(page_url)
if shortest_image_url:
    print(shortest_image_url)
barcode = "4513750119336"
page_url = f"https://chiikawamarket.jp/products/{barcode}"
shortest_image_url = fetch_shortest_image_url(page_url)
if shortest_image_url:
    print(shortest_image_url)
