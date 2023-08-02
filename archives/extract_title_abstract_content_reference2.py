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

def load_tags():
    with open('tags.json', 'r') as f:
        tags = json.load(f)
    return tags

def setup_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver

def extract_title(driver, tag_set):
    title = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["title"]))
    ).text
    return title

def extract_abstract(driver, tag_set):
    abstract = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["abstract"]))
    ).text
    return abstract

def extract_content(driver, tag_set):
    content = ''
    for selector in tag_set['content']:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            WebDriverWait(driver, 30).until_not(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), 'Loading...')
            )
            content += driver.find_element(By.CSS_SELECTOR, selector).text + "\n"
    return content

def get_reference_links(driver, tag_set):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    reference_links = soup.find_all('a', {'class': tag_set["css_class"]})

    links = []
    for link in reference_links:
        urls = link.get('href')
        links.append(urls)

    return links

def extract_info(driver, tag_set):
    title = extract_title(driver, tag_set)
    abstract = extract_abstract(driver, tag_set)
    content = extract_content(driver, tag_set)

    return title, abstract, content

def process_url(tags, url):
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
            f.write("Reference Links:\n")
            for link in references:
                f.write(link + "\n\n")
    except Exception as e:
        print(f"An error occurred while extracting data from {url}: {e}")

    driver.quit()

def process_urls(tags, urls):
    for url in urls:  
        process_url(tags, url)

def main():
    tags = load_tags()

    urls= [
        "https://peerj.com/articles/15572/",
        "https://www.sciencedirect.com/science/article/pii/S1361841513000182",
        "https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.14807"       
    ]

    if not os.path.exists('output'):
        os.makedirs('output')

    process_urls(tags, urls)

if __name__ == "__main__":
    main()
