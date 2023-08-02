from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import sqlite3
import requests

def load_tags():
    with open('tags.json', 'r') as f:
        tags = json.load(f)
    return tags

def setup_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver

def extract_title(driver, tag_set):
    try:
        title = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["title"]))
        ).text
        return title
    except Exception:
        print("Failed to extract title from the page.")
        return None

def extract_abstract(driver, tag_set):
    try:
        abstract = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["abstract"]))
        ).text
        return abstract
    except Exception:
        print("Failed to extract abstract from the page.")
        return None

def extract_content(driver, tag_set):
    content = ''
    try:
        for selector in tag_set['content']:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                WebDriverWait(driver, 30).until_not(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), 'Loading...')
                )
                content += driver.find_element(By.CSS_SELECTOR, selector).text + "\n"
        return content
    except Exception:
        print("Failed to extract content from the page.")
        return None
def setup_database():
    conn = sqlite3.connect('web_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS web_data 
        (url TEXT, title TEXT, abstract TEXT, content TEXT, reference_links TEXT)
    ''')
    conn.commit()
    conn.close()

    
def get_reference_links(driver, tag_set):
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        reference_links = soup.find_all('a', {'class': tag_set["css_class"]})
        links = []
        for link in reference_links:
            url = link.get('href')
            if url.startswith("http://doi.org") or url.startswith("https://doi.org"):
                response = requests.get(url, allow_redirects=True)
                url = response.url

            if url.startswith("https://linkinghub.elsevier.com"):
                driver.get(url)
                url = driver.current_url
                
            elif not (url.startswith("http") or url.startswith("www")):
                base_url = "{0.scheme}://{0.netloc}".format(urlsplit(driver.current_url))
                url = base_url + url

            links.append(url)
        return links
    except Exception as e:
        print(f"Failed to extract reference links from the page. Error: {e}")
        return None

def extract_info(driver, tag_set):
    title = extract_title(driver, tag_set)
    abstract = extract_abstract(driver, tag_set)
    content = extract_content(driver, tag_set)
    return title, abstract, content

from collections import deque

def process_url(tags, url, visited_urls):
    driver = setup_driver()
    domain = None
    for site in tags:
        if site in url:
            domain = site
            break
    if domain is None:
        print(f"Unsupported website: {url}. Please add the appropriate tag selectors to the JSON file.")
        driver.quit()
        return []
    tag_set = tags[domain]
    driver.get(url)
    reference_links = []
    try:
        title, abstract, content = extract_info(driver, tag_set)
        reference_links = get_reference_links(driver, tag_set)
        reference_links_str = "\n".join(reference_links)
        conn = sqlite3.connect('web_data.db')
        c = conn.cursor()
        c.execute("INSERT INTO web_data VALUES (?, ?, ?, ?, ?)", 
                  (url, title, abstract, content, reference_links_str))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"An error occurred while extracting data from {url}: {e}")
    driver.quit()
    return [link for link in reference_links if link not in visited_urls]

def process_urls(tags, urls):
    url_queue = deque(urls)
    visited_urls = set()
    while url_queue:
        url = url_queue.popleft()
        visited_urls.add(url)
        reference_links = process_url(tags, url, visited_urls)
        url_queue.extend(reference_links)

def setup_database():
    conn = sqlite3.connect('web_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS web_data 
        (url TEXT, title TEXT, abstract TEXT, content TEXT, reference_links TEXT)
    ''')
    conn.commit()
    conn.close()

def main():
    setup_database()
    tags = load_tags()
    urls= [
        "https://peerj.com/articles/15572/",     
    ]
    process_urls(tags, urls)

if __name__ == "__main__":
    main()
