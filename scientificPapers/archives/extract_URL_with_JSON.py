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
    if isinstance(tags, list):
        for tag in tags:
            WebDriverWait(driver, 30).until_not(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, tag), 'Loading...')
            )
            content += driver.find_element(By.CSS_SELECTOR, tag).text + "\n"
    else:
        WebDriverWait(driver, 30).until_not(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, tags), 'Loading...')
        )
        content = driver.find_element(By.CSS_SELECTOR, tags).text
    return content

def load_webpage(driver, url):
    """Loads a webpage from a given URL."""
    driver.get(url)

def main():
    # Load the tag data
    tags = load_tags()

    # Setting up the webdriver
    driver = setup_driver()

    # Define the list of URLs
    urls_2= [
        "https://www.sciencedirect.com/science/article/pii/S1574954122001443#preview-section-references",
        "https://www.sciencedirect.com/science/article/pii/S1361841513000182",
        "https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.14807"
    ]

    urls = []
    for url_2 in urls_2:
        url = url_2.split("#preview-section-references")[0]
        urls.append(url)

    print(urls)

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


            print("URL :", url)
            print("Title :", title)
            print("Abstract :", abstract)
            print("Content :", content)
        except Exception as e:
            print(f"An error occurred while extracting data from {url}: {e}")

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
