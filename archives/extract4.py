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

def extract_reference(driver, tag_set):
    """Extracts and returns the abstract from the webpage."""
    reference = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["reference"]))
    ).text
    return reference

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



def extract_info(driver, tag_set):
    """Extracts and returns the title, abstract, content, and references from the webpage."""
    try:
        title = extract_title(driver, tag_set)
    except Exception as e:
        print(f"An error occurred while extracting title: {e}")
        return

    try:
        abstract = extract_abstract(driver, tag_set)
    except Exception as e:
        print(f"An error occurred while extracting abstract: {e}")
        return

    try:
        content = extract_content(driver, tag_set)
    except Exception as e:
        print(f"An error occurred while extracting content: {e}")
        return

    try:
        reference = extract_reference(driver, tag_set)
    except Exception as e:
        print(f"An error occurred while extracting references: {e}")
        return

    return title, abstract, content, reference


def main():
    # Load the tag data
    tags = load_tags()

    # Define the list of URLs
    urls= [
        "https://www.sciencedirect.com/science/article/pii/S1574954122001443#preview-section-references",
        "https://www.sciencedirect.com/science/article/pii/S1361841513000182",
        "https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.14919",
        "https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.14807",
        "https://onlinelibrary.wiley.com/doi/full/10.1002/cpe.7842",
        "https://peerj.com/articles/15572/"       
    ]

    # Ensure output directory exists
    if not os.path.exists('output'):
        os.makedirs('output')

    # Loop over the list of URLs
    for url in urls:  
        # Setting up the webdriver
        driver = setup_driver()

        # Based on the URL, choose the appropriate tag set
        domain = None
        for site in tags:
            if site in url:
                domain = site
                break

        if domain is None:
            print(f"Unsupported website: {url}. Please add the appropriate tag selectors to the JSON file.")
            continue

        tag_set = tags[domain]

        # Load the webpage
        driver.get(url)

        # Extract and print the title, abstract, and content
        try:
            title, abstract, content, reference = extract_info(driver, tag_set)

            # Prepare filename from title and store the data
            filename = title.replace(' ', '_').replace(':', '').replace('/', '') + '.txt'
            with open(os.path.join('output', filename), 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\nTitle: {title}\nAbstract: {abstract}\nContent: {content}\nReference: {reference}\n")
        except Exception as e:
            print(f"An error occurred while extracting data from {url}: {e}")

        # Close the browser after each URL
        driver.quit()

if __name__ == "__main__":
    main()
