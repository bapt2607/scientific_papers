from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    """Configures and returns the WebDriver."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver


def load_webpage(driver, url):
    """Loads a webpage from a given URL."""
    driver.get(url)


def extract_title(driver):
    """Extracts and returns the title of the article."""
    title = driver.find_element(By.CSS_SELECTOR,'span.title-text').text
    return title


def extract_abstract(driver):
    """Extracts and returns the abstract of the article."""
    abstract = driver.find_element(By.CSS_SELECTOR, '.abstract.author').text
    return abstract


def extract_content(driver):
    """Extracts and returns the main content of the article."""
    # Wait for the text of the element to change from 'Loading...'
    WebDriverWait(driver, 30).until_not(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'div.Body.u-font-gulliver.text-s#body'), 'Loading...')
    )

    # Re-obtain the main content element and extract the text
    content = driver.find_element(By.CSS_SELECTOR, 'div.Body.u-font-gulliver.text-s#body').text
    return content


def main():
    # Setting up the webdriver
    driver = setup_driver()

    # Define the URL of the article
    url = "https://www.sciencedirect.com/science/article/pii/S1361841513000182"

    # Load the webpage
    load_webpage(driver, url)

    # Extract the title, abstract, and content
    try:
        title = extract_title(driver)
        abstract = extract_abstract(driver)
        content = extract_content(driver)

        print("Title :", title)
        print("Abstract :", abstract)
        print("Content :", content)
    except Exception as e:
        print(f"An error occurred while extracting data: {e}")
    finally:
        # Close the browser
        driver.quit()


if __name__ == "__main__":
    main()
