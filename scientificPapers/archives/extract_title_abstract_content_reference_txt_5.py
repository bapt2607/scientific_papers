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

import requests
def load_tags():
    # Loading tag selectors from a JSON file
    with open('tags.json', 'r') as f:
        tags = json.load(f)
    return tags

def setup_driver():
    # Setup for Chrome WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver

def extract_title(driver, tag_set):
    # Extracting title from the webpage
    try:
        title = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["title"]))
        ).text
        return title
    except Exception:
        print("Failed to extract title from the page.")
        return None

def extract_abstract(driver, tag_set):
    # Extracting abstract from the webpage
    try:
        abstract = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["abstract"]))
        ).text
        return abstract
    except Exception:
        print("Failed to extract abstract from the page.")
        return None
    
    
def extract_content(driver, tag_set):
    # Extracting content from the webpage
    try:
        WebDriverWait(driver, 60).until_not(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, tag_set["content"]), "Loading...")
        )
        content = driver.find_element(By.CSS_SELECTOR, tag_set["content"]).text
        return content
    except Exception as e:
        print(f"Failed to extract content from the page due to {str(e)}.")
        return None


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
    # Extracting all necessary information from the webpage
    title = extract_title(driver, tag_set)
    abstract = extract_abstract(driver, tag_set)
    content = extract_content(driver, tag_set)
    return title, abstract, content

def process_url(tags, url):
    # Processing each URL
    driver = setup_driver()
    domain = None
    for site in tags:
        if site in url:
            domain = site
            break
    if domain is None:
        print(f"Unsupported website: {url}. Please add the appropriate tag selectors to the JSON file.")
        driver.quit()
        return
    tag_set = tags[domain]
    driver.get(url)
    try:
        title, abstract, content = extract_info(driver, tag_set)
        references = get_reference_links(driver, tag_set)
        filename = title.replace(' ', '_').replace(':', '').replace('/', '') + '.txt'
        with open(os.path.join('output', filename), 'w', encoding='utf-8') as f:
            f.write(f"URL: {url}\nTitle: {title}\nAbstract: {abstract}\nContent: {content}\n")

        # Check if the links already exist in the file
        link_file_path = os.path.join('output', 'all_links.txt')
        existing_links = []
        if os.path.exists(link_file_path):
            with open(link_file_path, 'r', encoding='utf-8') as linkfile:
                existing_links = linkfile.readlines()

        # Write reference links to a separate file
        with open(link_file_path, 'a', encoding='utf-8') as linkfile:
            for link in references:
                if link + "\n" not in existing_links:
                    linkfile.write(link + "\n")
    except Exception as e:
        print(f"An error occurred while extracting data from {url}: {e}")
    driver.quit()



def process_urls(tags, urls):
    # Processing a list of URLs
    for url in urls:  
        process_url(tags, url)

def main():
    tags = load_tags()
    last_line_processed = 0
    while True:
        with open('output/all_links.txt', 'r') as f:
            lines = f.read().splitlines()
            new_lines = lines[last_line_processed:]
            for url in new_lines:
                process_url(tags, url)
                last_line_processed += 1
        time.sleep(1)  # Wait for a second before checking the file again

if __name__ == "__main__":
    main()