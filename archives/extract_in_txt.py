import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


def setup_driver():
    """Configures and returns the WebDriver."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver



def load_tags():
    """Loads and returns the tag data from the JSON file."""
    with open('tags.json', 'r') as f:
        tags = json.load(f)
    return tags

def extract_title(driver, tag):
    """Extracts and returns the title of the article."""
    title = driver.find_element(By.CSS_SELECTOR,tag).text
    return title

def extract_abstract(driver, tag):
    """Extracts and returns the abstract of the article."""
    abstract = driver.find_element(By.CSS_SELECTOR, tag).text
    return abstract

def extract_content(driver, tags):
    """Extracts and returns the main content of the article."""
    content = ""
    
    for tag in tags:
        if isinstance(tag, list):
            for subtag in tag:
                try:
                    WebDriverWait(driver, 30).until_not(
                        EC.text_to_be_present_in_element((By.CSS_SELECTOR, subtag), 'Loading...')
                    )
                    content += driver.find_element(By.CSS_SELECTOR, subtag).text + "\n"
                except Exception as e:
                    print(f"An error occurred while trying to extract content with tag {subtag}: {e}")
        else:
            try:
                WebDriverWait(driver, 30).until_not(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, tag), 'Loading...')
                )
                content = driver.find_element(By.CSS_SELECTOR, tag).text
            except Exception as e:
                print(f"An error occurred while trying to extract content with tag {tag}: {e}")
    return content


def load_webpage(driver, url):
    """Loads a webpage from a given URL."""
    driver.get(url)



def write_to_file(url, title, abstract, content):
    # sanitize the url to use it as a filename
    filename = re.sub(r'\W+', '', url) + '.txt'
    
    # check if file already exists, if so append a number to it
    if os.path.isfile(filename):
        i = 1
        while os.path.isfile(filename[:-4] + str(i) + '.txt'):
            i += 1
        filename = filename[:-4] + str(i) + '.txt'

    with open(filename, 'w') as file:
        file.write(f'URL: {url}\n')
        file.write(f'Title: {title}\n')
        file.write(f'Abstract: {abstract}\n')
        file.write(f'Content: {content}\n')

# Modify main function to call write_to_file function
def main():
    # Load the tag data
    tags = load_tags()

    # Setting up the webdriver
    driver = setup_driver()

    # Define the list of URLs
    urls = [
        "https://www.sciencedirect.com/science/article/pii/S1574954122001443#preview-section-references",
        "https://www.sciencedirect.com/science/article/pii/S1361841513000182",
        "https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.14807"
    ]

    # Loop over the list of URLs
    for url in urls:
        # Based on the URL, choose the appropriate tag set
        if "sciencedirect" and "preview-section-references" in url:
            tag_set = tags["sciencedirect_preview"]
        elif "sciencedirect" in url:
            tag_set = tags["sciencedirect"]
        elif "wiley" in url:
            tag_set = tags["wiley"]
        else:
            print(f"Unsupported website: {url}")
            continue

        # Load the webpage
        load_webpage(driver, url)

        # Extract the title, abstract, and content
        try:
            title = extract_title(driver, tag_set["title"])
            abstract = extract_abstract(driver, tag_set["abstract"])
            content = extract_content(driver, tag_set["content"])

            write_to_file(url, title, abstract, content)

        except Exception as e:
            print(f"An error occurred while extracting data from {url}: {e}")

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
