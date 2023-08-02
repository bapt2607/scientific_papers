from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time

def load_tags():
    """Loads and returns the tag data from the JSON file."""
    with open('tags.json', 'r') as f:
        tags = json.load(f)
    return tags

def setup_driver():
    """Configures and returns the WebDriver."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver

def extract_title(driver, tag_set):
    """Extracts and returns the title from the webpage."""
    title = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["title"]))
    ).text
    return title

def extract_abstract(driver, tag_set):
    """Extracts and returns the abstract from the webpage."""
    abstract = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["abstract"]))
    ).text
    return abstract

def extract_content(driver, tag_set):
    """Extracts and returns the content from the webpage."""
    content = ''
    # Loop over all content selectors
    for selector in tag_set['content']:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            WebDriverWait(driver, 30).until_not(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), 'Loading...')
            )
            content += driver.find_element(By.CSS_SELECTOR, selector).text + "\n"
    return content


def extract_references(driver, tag_set):
    """Extracts and returns the reference links from the webpage."""
    reference_section = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["reference_scholar"]))
    )
    references = reference_section.find_elements(By.CSS_SELECTOR, tag_set["reference_link_scholar"])

    gs_links = [reference.get_attribute('href') for reference in references if 'scholar.google' in reference.get_attribute('href')]
    return "\n".join(gs_links)

def extract_info(driver, tag_set):
    """Extracts and returns the title, abstract, content, and reference links from the webpage."""
    title = extract_title(driver, tag_set)
    abstract = extract_abstract(driver, tag_set)
    content = extract_content(driver, tag_set)
    reference_links = extract_references(driver, tag_set)

    return title, abstract, content, reference_links

def main():
    tags = load_tags()
    urls = [
        "https://www.sciencedirect.com/science/article/pii/S1361841513000182"
        ]
    if not os.path.exists('output'):
        os.makedirs('output')
    for url in urls:  
        driver = setup_driver()
        domain = None
        for site in tags:
            if site in url:
                domain = site
                break
        if domain is None:
            print(f"Unsupported website: {url}. Please add the appropriate tag selectors to the JSON file.")
            continue
        tag_set = tags[domain]
        driver.get(url)
        try:
            title, abstract, content, reference_links = extract_info(driver, tag_set)
            filename = title.replace(' ', '_').replace(':', '').replace('/', '') + '.txt'
            with open(os.path.join('output', filename), 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\nTitle: {title}\nAbstract: {abstract}\nContent: {content}\nReferences: {reference_links}\n")
        except Exception as e:
            print(f"An error occurred while extracting data from {url}: {e}")
        driver.quit()

if __name__ == "__main__":
    main()
