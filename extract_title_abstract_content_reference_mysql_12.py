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

# Function to insert extracted data into the 'articles' table in the database
def insert_into_authors_database(connection, first_name, last_name, affiliation, email ):
    cursor = connection.cursor()
    query = """
    INSERT INTO authors (first_name, last_name, affiliation, email ) 
    VALUES (%s, %s,%s, %s)
    """
    # If title, abstract or content is None, replace it with an empty string
    values = (first_name, last_name, affiliation, email )
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

def insert_into_authorarticle_database(connection, author_id, article_id):
    cursor = connection.cursor()
    query = """
    INSERT INTO AuthorArticle (author_id, article_id) 
    VALUES (%s, %s)
    """
    values = (author_id, article_id)
    try:
        cursor.execute(query, values)
        connection.commit()
        print("AuthorArticle data inserted successfully")
        return cursor.lastrowid
    except Exception as err:
        print(f"Error: '{err}'")
        return None
    finally:
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
    
# Sub-function to extract first name from author element
def extract_first_name(author, tag_set):
    try:
        first_name = author.find_element(By.CSS_SELECTOR, tag_set["first_name"]).text
        return first_name
    except Exception:
        print("Failed to extract first name from the author info.")
        return None

# Sub-function to extract last name from author element
def extract_last_name(author, tag_set):
    try:
        last_name = author.find_element(By.CSS_SELECTOR, tag_set["last_name"]).text
        return last_name
    except Exception:
        print("Failed to extract last name from the author info.")
        return None

# Sub-function to extract affiliation from author element
def extract_affiliation(author, tag_set):
    try:
        affiliation = author.find_element(By.CSS_SELECTOR, tag_set["affiliation"]).text
        return affiliation
    except Exception:
        print("Failed to extract affiliation from the author info.")
        return None

# Sub-function to extract email from author element
def extract_email(author, tag_set):
    try:
        email_element = author.find_element(By.CSS_SELECTOR, tag_set["email"])
        email = email_element.get_attribute('href')
        if email.startswith('mailto:'):
            email = email[7:]  # remove 'mailto:' from the beginning
        return email
    except Exception:
        print("Failed to extract email from the author info.")
        return None


# Function to extract author information from webpage
def extract_authors_info(driver, tag_set):
    authors_info = []
    try:
        authors_elements = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, tag_set["author"]))
        )
        for author in authors_elements:
            driver.execute_script("arguments[0].scrollIntoView();", author)
            first_name = extract_first_name(author, tag_set)
            last_name = extract_last_name(author, tag_set)
            affiliation = extract_affiliation(author, tag_set)
            email = extract_email(author, tag_set)
            authors_info.append((first_name, last_name, affiliation, email))
        return authors_info
    except Exception as e:
        print("Failed to extract authors info from the page.")
        print(f"Error: {e}")
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
    reference_extraction_successful = False  # initialize reference_extraction_successful here
    try:
        title, abstract, content = extract_info(driver, tag_set)
        extraction_successful = all([title, abstract, content])
    except Exception as e:
        print(f"An error occurred while extracting data from {url}: {e}")
        title, abstract, content = None, None, None
        extraction_successful = False

    try:
        references = get_reference_links(driver, tag_set)
        reference_extraction_successful = bool(references)  # update reference_extraction_successful here
    except Exception as e:
        print(f"An error occurred while extracting reference links from {url}: {e}")
        references = []
        reference_extraction_successful = False

    source_id = insert_into_database(connection, url, title, abstract, content, extraction_successful, reference_extraction_successful)
    try:
        authors = extract_authors_info(driver, tag_set)
    except Exception as e:
        print(f"An error occurred while extracting authors from {url}: {e}")
        authors = None

    if authors:
        for author in authors:
            first_name, last_name, affiliation, email = author
            author_id = insert_into_authors_database(connection, first_name, last_name, affiliation, email)
            if author_id is not None:
                insert_into_authorarticle_database(connection, author_id, source_id)

    
    try:
        references = get_reference_links(driver, tag_set)
        reference_extraction_successful = bool(references)  # update reference_extraction_successful here
    except Exception as e:
        print(f"An error occurred while extracting reference links from {url}: {e}")
        references = []
        reference_extraction_successful = False

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