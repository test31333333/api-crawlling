from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import os

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')  
chrome_options.add_argument('--incognito') 
driver = webdriver.Chrome(service=Service('C:\\Windows\\chromedriver-win64\\chromedriver.exe'), options=chrome_options)

driver.get('https://www.aljazeera.net/politics/')

def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

time.sleep(2)
scroll_to_bottom()

def get_articles():
    articles = driver.find_elements(By.CSS_SELECTOR, 'article')  
    links = []
    for article in articles:
        try:
            link = article.find_element(By.TAG_NAME, 'a').get_attribute('href')
            links.append(link)
        except:
            continue
    return links

click_count = 0
while True:
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.show-more-button.big-margin'))
        )
        button.click()
        click_count += 1
        print(f'Button clicked {click_count} times.')

        if click_count >= 5:
            print("Skipping this stage after 5 clicks.")
            break

        time.sleep(5)
        scroll_to_bottom()
        time.sleep(10)

    except Exception as e:
        print("No more 'Show More' button or error:", e)
        break

new_links = get_articles()

old_links = []
if os.path.exists("kk.json"):
    with open("kk.json", "r", encoding="utf-8") as file:
        old_links = json.load(file)

combined_links = list(set(old_links + new_links))

with open("kk.json", "w", encoding="utf-8") as file:
    json.dump(combined_links, file, ensure_ascii=False, indent=4)

print(f"{len(combined_links)} links have been saved to kk.json (after merging only the new ones).")

driver.quit()
