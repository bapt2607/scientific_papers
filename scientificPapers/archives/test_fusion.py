import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_css_class(site, config):
    """Retrieve the CSS class for a given site from the configuration."""
    return config[site]['css_class']

def get_page_content(url):
    """Load a webpage and return its content."""
    # Configure Selenium to use Chrome
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service)

    # Navigate to the web page with Selenium
    driver.get(url)

    # Allow the browser to load the page
    time.sleep(5)

    # Get the content of the page with Selenium
    html = driver.page_source

    # Close the browser
    driver.quit()

    return html

def parse_links(html, css_class):
    """Parse the webpage content and return the URLs of all links with the given CSS class."""
    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Find all <a> links on the page with the specific class
    reference_links = soup.find_all('a', {'class': css_class})

    # List to store the reference links
    links = []

    # Go through the links and get the URLs
    for link in reference_links:
        url = link.get('href')
        links.append(url)

    return links

def main():
    # Read the JSON configuration file
    with open('config.json') as f:
        config = json.load(f)

    # Define the URLs in the script
    urls = {
        "sciencedirect": "https://www.sciencedirect.com/science/article/pii/S2212671614001024",
        "peerj": "https://peerj.com/articles/15572/"
    }

    # For each site in the configuration
    for site in config:
        css_class = get_css_class(site, config)
        url = urls[site]

        # Get the page content
        html = get_page_content(url)

        # Parse the reference links
        references = parse_links(html, css_class)

        # Print the reference links
        print(f"References for {site}:")
        for reference in references:
            print(reference)

if __name__ == "__main__":
    main()
