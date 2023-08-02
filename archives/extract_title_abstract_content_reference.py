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

def get_reference_links(urls, tag_set):
    # Configurez Selenium pour utiliser Chrome
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service)

    # Accédez à la page Web avec Selenium
    driver.get(urls)

    # Laissez le navigateur charger la page
    time.sleep(5)

    # Obtenez le contenu de la page avec Selenium
    html = driver.page_source

    # Utilisez BeautifulSoup pour analyser le HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Trouvez tous les liens <a> dans la page avec la classe spécifique
    reference_links = soup.find_all('a', {'class': tag_set["css_class"]})

    # Liste pour stocker les liens des références
    links = []

    # Parcourez les liens et obtenez les URLs
    for link in reference_links:
        urls = link.get('href')
        links.append(urls)

    # Fermez le navigateur
    driver.quit()

    return links


def extract_info(driver, tag_set):
    """Extracts and returns the title, abstract, and content from the webpage."""
    title = extract_title(driver, tag_set)
    abstract = extract_abstract(driver, tag_set)
    content = extract_content(driver, tag_set)

    return title, abstract, content



def process_url(tags, url):
    """Processes a single URL."""
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
        driver.quit()
        return

    tag_set = tags[domain]

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

    # Close the browser after processing URL
    driver.quit()


def process_urls(tags, urls):
    """Processes a list of URLs."""
    # Loop over the list of URLs
    for url in urls:  
        process_url(tags, url)


def main():
    # Load the tag data
    tags = load_tags()

    # Define the list of URLs
    urls= [
        "https://peerj.com/articles/15572/"       
    ]

    # Ensure output directory exists
    if not os.path.exists('output'):
        os.makedirs('output')

    process_urls(tags, urls)
    
    # Based on the URL, choose the appropriate tag set
    domain = None
    for site in tags:
        if site in urls[0]: # assuming the same domain for all URLs
            domain = site
            break

    if domain is None:
        print(f"Unsupported website: {urls[0]}. Please add the appropriate tag selectors to the JSON file.")
        return

    tag_set = tags[domain]
    
    references = get_reference_links(urls[0], tag_set)  # assuming the first URL is representative

    # Affichage des liens des références
    for reference in references:
        print(reference)

if __name__ == "__main__":
    main()
