# Import necessary libraries
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
from urllib.parse import urlsplit
import requests
import mysql.connector

# Function to create connection to MySQL database
def create_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",  
            user="root",  
            passwd="12345678",  
            database="database_name"  
        )
        print("MySQL Database connection successful")
    except Exception as err:
        print(f"Error: '{err}'")

    return connection

# Function to insert extracted data into the 'articles' table in the database
def insert_into_database(connection, url, title, abstract, content, extraction_successful, reference_extraction_successful):
    cursor = connection.cursor()
    query = """
    INSERT INTO articles (url, title, abstract, content, extraction_successful, reference_extraction_successful) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    # If title, abstract or content is None, replace it with an empty string
    values = (url, title if title is not None else "None", abstract if abstract is not None else "None", content if content is not None else "None", extraction_successful, reference_extraction_successful)
    try:
        cursor.execute(query, values)
        connection.commit()
        print("Data inserted successfully")
        return cursor.lastrowid
    except Exception as err:
        print(f"Error: '{err}'")
        return None
    finally:
        cursor.close()




# Function to insert links into 'links' table in the database
def insert_links_into_database(connection, source_id, references):
    cursor = connection.cursor()
    query = """
    INSERT INTO links (source_id, reference_url) VALUES (%s, %s)
    """
    for link in references:
        values = (source_id, link)
        try:
            cursor.execute(query, values)
            connection.commit()
            print("Link inserted successfully")
        except Exception as err:
            print(f"Error: '{err}'")

    cursor.close()



# Function to load tags from JSON file
def load_tags():
    with open('tags.json', 'r') as f:
        tags = json.load(f)
    return tags

# Function to set up webdriver for Selenium
def setup_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver

# Function to extract title from webpage
def extract_title(driver, tag_set):
    try:
        title = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["title"]))
        ).text
        return title
    except Exception:
        print("Failed to extract title from the page.")
        return None

# Function to extract abstract from webpage
def extract_abstract(driver, tag_set):
    try:
        abstract = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["abstract"]))
        ).text
        return abstract
    except Exception:
        print("Failed to extract abstract from the page.")
        return None

# Function to extract content from webpage
def extract_content(driver, tag_set):
    try:
        WebDriverWait(driver, 60).until(
            lambda d: d.find_element(By.CSS_SELECTOR, tag_set["content"]).text != "Loading..."
        )
        content = driver.find_element(By.CSS_SELECTOR, tag_set["content"]).text
        return content
    except Exception as e:
        print(f"Failed to extract content from the page.")
        return None

# Function to extract reference links from webpage
def get_reference_links(driver, tag_set):
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        reference_links = soup.find_all('a', {'class': tag_set["css_class"]})
        links = []
        for link in reference_links:
            url = link.get('href')
            if url.startswith("http://doi.org") or url.startswith("https://doi.org"):
                response = requests.get(url, allow_redirects=True)
                url = response.url

            if url.startswith("https://linkinghub.elsevier.com"):
                driver.get(url)
                url = driver.current_url

            elif not (url.startswith("http") or url.startswith("www")):
                base_url = "{0.scheme}://{0.netloc}".format(urlsplit(driver.current_url))
                url = base_url + url
            
            url = url.replace("?via%3Dihub", "")

            links.append(url)
        return links
    except Exception as e:
        print(f"Failed to extract reference links from the page. Error: {e}")
        return None

# Function to extract information from webpage
def extract_info(driver, tag_set):
    title = extract_title(driver, tag_set)
    abstract = extract_abstract(driver, tag_set)
    content = extract_content(driver, tag_set)
    return title, abstract, content

# Function to process URL and extract information
def process_url(tags, url, connection):
    driver = setup_driver()
    domain = None
    for site in tags:
        if site in url:
            domain = site
            break
    if domain is None:
        print(f"Unsupported website: {url}. Please add the appropriate tag selectors to the JSON file.")
        # insert URL into database even if unsupported
        insert_into_database(connection, url, None, None, None, False, False)
        driver.quit()
        return
    tag_set = tags[domain]
    driver.get(url)
    try:
        title, abstract, content = extract_info(driver, tag_set)
        extraction_successful = all([title, abstract, content])
    except Exception as e:
        print(f"An error occurred while extracting data from {url}: {e}")
        title, abstract, content = None, None, None
        extraction_successful = False
    try:
        references = get_reference_links(driver, tag_set)
        reference_extraction_successful = bool(references)
    except Exception as e:
        print(f"An error occurred while extracting reference links from {url}: {e}")
        references = []
        reference_extraction_successful = False
    source_id = insert_into_database(connection, url, title, abstract, content, extraction_successful, reference_extraction_successful)
    if references:
        insert_links_into_database(connection, source_id, references)
    driver.quit()


# Function to process multiple URLs and extract information
def process_urls(tags, urls, connection):
    for url in urls:  
        process_url(tags, url, connection)

# Function to get URL from database using an ID
def get_url_from_db(connection, id):
    cursor = connection.cursor()
    query = f"SELECT reference_url FROM links WHERE id = {id};"
    cursor.execute(query)
    result = cursor.fetchall()  # Retrieve all records from the query
    cursor.close()  # Close the cursor once you're done with it
    return result[0][0] if result else None  # Extract the URL from the first tuple, if available

# Function to check if URL is already in the 'articles' table
def check_url_in_articles(connection, url):
    cursor = connection.cursor()
    query = f"SELECT url FROM articles WHERE url = '{url}';"
    cursor.execute(query)
    result = cursor.fetchall()  # Retrieve all records from the query
    cursor.close()  # Close the cursor once you're done with it
    return bool(result)  # Returns True if the URL is in the 'articles' table, False otherwise

# Main function

def main():
    connection = create_db_connection() 
    tags = load_tags()

    if not os.path.exists('output'):
        os.makedirs('output')

    for id in range(1, 13):  # Iterate over numbers from 1 to 10
        url = get_url_from_db(connection, id)  # Obtenez l'URL de la base de données
        print(url,"\n")
        if url and not check_url_in_articles(connection, url):  
            process_url(tags, url, connection) 
        else:
            print(f"URL {url} is already processed.")

if __name__ == "__main__":
    main()