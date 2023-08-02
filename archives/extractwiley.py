from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
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
    for selector in tag_set['content']:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            WebDriverWait(driver, 30).until_not(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), 'Loading...')
            )
            content += driver.find_element(By.CSS_SELECTOR, selector).text + "\n"
    return content

def close_cookie_banner(driver):
    """Closes the cookie banner if it exists."""
    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.osano-cm-accept-all'))
        )
        close_button.click()
        time.sleep(2)  # Wait for the banner to close
    except Exception as e:
        print(f"An error occurred while closing the cookie banner: {e}")


def extract_references(driver, tag_set):
    """Extracts and returns the reference links from the webpage."""
    close_cookie_banner(driver)
    # Slowly scroll until the reference button is visible
    reference_button = None
    y = 500
    while reference_button is None:
        driver.execute_script(f"window.scrollTo(0, {y})")
        y += 500  
        time.sleep(1)
        try:
            reference_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["reference_button"]))
            )
        except:
            continue

    # Click to expand references using JavaScript
    driver.execute_script("arguments[0].click();", reference_button)

    reference_section = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["reference"]))
    )

    references = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, tag_set["reference_link"]))
    )

    gs_links = [reference.get_attribute('href') for reference in references if 'scholar.google' in reference.get_attribute('href')]
    return "\n".join(gs_links)


def extract_info(driver, tag_set):
    """Extracts and returns the title, abstract, content, and reference links from the webpage."""
    print("Extracting title...")
    title = extract_title(driver, tag_set)
    print("Extracting abstract...")
    abstract = extract_abstract(driver, tag_set)
    print("Extracting content...")
    content = extract_content(driver, tag_set)
    print("Extracting references...")
    reference_links = extract_references(driver, tag_set)

    return title, abstract, content, reference_links


def main():
    tags = load_tags()
    urls = [
        "https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.14919"
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
