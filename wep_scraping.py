import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import json
import os

def load_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Failed to load page: {url}\nError: {e}")
        return None

def show_article_info(url, article_info_list, current_id):
    soup = load_page(url)
    if soup is None:
        return article_info_list

    article_info = {}
    article_info["id"] = current_id 
    article_info["URL"] = url

    topics = soup.find("div", class_="topics")
    if topics:
        article_info["Topics"] = topics.text.strip()

    title = soup.find("h1")
    if title:
        article_info["Title"] = title.text.strip()

    date_span = soup.find("span", style="color: var(--main-orange);")
    if date_span:
        article_info["Date"] = date_span.get_text(strip=True)

    image = soup.find("img")
    if image and image.get("src"):
        article_info["Image URL"] = urljoin(url, image["src"])

    author = soup.find("span", class_="article-author-name-item")
    if author:
        article_info["Author"] = author.text.strip()

    paragraphs = soup.find_all("p")
    if paragraphs:
        content = "\n".join(p.text.strip() for p in paragraphs)
        article_info["Content"] = content

    if article_info:
        article_info_list.append(article_info)

    return article_info_list

def start_scraping(url_list):
    existing_articles = []
    existing_urls = set()
    max_id = 0

    if os.path.exists('test.json'):
        try:
            with open('test.json', 'r', encoding='utf-8') as f:
                existing_articles = json.load(f)
                for article in existing_articles:
                    existing_urls.add(article.get("URL", ""))
                    if "id" in article and isinstance(article["id"], int):
                        max_id = max(max_id, article["id"])
        except Exception as e:
            print(f"Failed to load existing data: {e}")

    new_articles = []
    current_id = max_id + 1

    for link in url_list:
        if link in existing_urls:
            print(f"Skipping already processed link: {link}")
            continue
        show_article_info(link, new_articles, current_id)
        current_id += 1
        time.sleep(1)

    all_articles = existing_articles + new_articles

    with open('test.json', 'w', encoding='utf-8') as file:
        json.dump(all_articles, file, ensure_ascii=False, indent=4)

def download_images_from_json(json_file='test.json', save_folder='downloaded_images'):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        os.makedirs(save_folder, exist_ok=True)

        for i, article in enumerate(data):
            img_url = article.get('Image URL')
            if not img_url:
                continue
            try:
                img_data = requests.get(img_url).content
                file_extension = os.path.splitext(img_url)[-1].split('?')[0] or '.jpg'
                filename = os.path.join(save_folder, f'image_{i}{file_extension}')
                with open(filename, 'wb') as img_file:
                    img_file.write(img_data)
                print(f'Downloaded {filename}')
            except Exception as e:
                print(f'Failed to download {img_url}: {e}')
    except Exception as e:
        print(f"Error loading or processing JSON file: {e}")

def load_json_data():
    try:
        with open('kk.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load JSON file: {e}")
        return []

links = load_json_data()
start_scraping(links)
print("Scraping completed. Data saved to test.json")
download_images_from_json("test.json")
