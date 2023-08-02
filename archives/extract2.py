from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os

def load_tags():
    """Loads and returns the tag data from the JSON file."""
    with open('tags.json', 'r') as f:
        tags = json.load(f)
    return tags

def setup_driver():
    """Configures and returns the WebDriver."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver

def extract_info(driver, tag_set):
    """Extracts and returns the title, abstract, and content from the webpage."""
    title = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["title"]))
    ).text

    abstract = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["abstract"]))
    ).text

    content = ''

    # Check if the first content selector exists
    first_selector = tag_set['content'][0]
    elements = driver.find_elements(By.CSS_SELECTOR, first_selector)
    if elements:
        WebDriverWait(driver, 30).until_not(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, first_selector), 'Loading...')
        )
        content = driver.find_element(By.CSS_SELECTOR, first_selector).text
    else:
        # Check if the second content selector exists before attempting to retrieve the third
        second_selector = tag_set['content'][1]
        elements = driver.find_elements(By.CSS_SELECTOR, second_selector)
        if elements:
            for tag in tag_set['content'][1:]:
                WebDriverWait(driver, 30).until_not(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, tag), 'Loading...')
                )
                content += driver.find_element(By.CSS_SELECTOR, tag).text + "\n"
    return title, abstract, content



def main():
    # Load the tag data
    tags = load_tags()

    # Setting up the webdriver
    driver = setup_driver()

    # Define the list of URLs
    urls= [
        #"https://www.sciencedirect.com/science/article/pii/S1574954122001443#preview-section-references",
        #"https://www.sciencedirect.com/science/article/pii/S1361841513000182",
        #"https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.14919",
        "https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.14807"
        "https://onlinelibrary.wiley.com/doi/full/10.1002/cpe.7842",
                
    ]

    # Ensure output directory exists
    if not os.path.exists('output'):
        os.makedirs('output')

    # Loop over the list of URLs
    for url in urls:
        # Remove "#preview-section-references" from the URL if present
        url = url.split("#")[0]
        
        # Based on the URL, choose the appropriate tag set
        if "sciencedirect" in url:
            tag_set = tags["sciencedirect"]
        elif "wiley" in url:
            tag_set = tags["wiley"]
        else:
            print(f"Unsupported website: {url}")
            continue

        # Load the webpage
        driver.get(url)

        # Extract and print the title, abstract, and content
        try:
            title, abstract, content = extract_info(driver, tag_set)

            # Prepare filename from title and store the data
            filename = title.replace(' ', '_').replace(':', '').replace('/', '') + '.txt'
            with open(os.path.join('output', filename), 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\nTitle: {title}\nAbstract: {abstract}\nContent: {content}\n")
        except Exception as e:
            print(f"An error occurred while extracting data from {url}: {e}")

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
