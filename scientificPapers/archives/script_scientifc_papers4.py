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

#website all extract: sciencedirect, peerj, aacrjournals
# no author: frontiers
# no reference: wiley
# no abstract & reference & authors: dovepress
# probleme cookies: academic


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

def update_into_database(connection, url, title, abstract, content, parsed, reference_parsed):
    cursor = connection.cursor()

    # Get the id from the database using the URL
    cursor.execute("SELECT id FROM articles WHERE url = %s", (url,))
    article_id = cursor.fetchone()
    if article_id:
        article_id = article_id[0]
    else:
        print(f"No record found for URL: {url}")
        cursor.close()
        return None
    
    query = """
    UPDATE articles 
    SET title = %s, abstract = %s, content = %s, parsed = %s, reference_parsed = %s
    WHERE id = %s
    """
    values = (title if title is not None else "None", abstract if abstract is not None else "None", content if content is not None else "None", parsed, reference_parsed, article_id)

    try:
        cursor.execute(query, values)
        connection.commit()
        print(f"Record for URL: {url} updated successfully")
    except Exception as err:
        print(f"Error: '{err}'")
    finally:
        cursor.close()

    return article_id


def insert_reference_links_into_database(connection, original_article_id, reference_links):
    cursor = connection.cursor()

    query = """
    INSERT INTO articles (url, original_article_id) 
    VALUES (%s, %s)
    """

    for url in reference_links:
        values = (url, original_article_id)

        try:
            cursor.execute(query, values)
            connection.commit()
            print(f"Record for URL: {url} inserted successfully with original article ID: {original_article_id}")
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

def insert_author_article_relation(connection, author_id, article_id):
    cursor = connection.cursor()
    query = "INSERT INTO author_article (author_id, article_id) VALUES (%s, %s);"
    values = (author_id, article_id)
    try:
        cursor.execute(query, values)
        connection.commit()
    except Exception as err:
        print(f"Error: '{err}'")
    finally:
        cursor.close()




def update_reference_extraction_status(connection, source_id, status):
    cursor = connection.cursor()
    query = """
    UPDATE articles
    SET reference_parsed = %s
    WHERE id = %s
    """
    values = (status, source_id)
    try:
        cursor.execute(query, values)
        connection.commit()
        print("Reference extraction status updated successfully")
    except Exception as err:
        print(f"Error: '{err}'")
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
        full_name = author.find_element(By.CSS_SELECTOR, tag_set["first_name"]).text
        first_name = full_name.split(' ')[0]
        return first_name
    except Exception:
        print("Failed to extract first name from the author info.")
        return None

# Sub-function to extract last name from author element
def extract_last_name(author, tag_set):
    try:
        full_name = author.find_element(By.CSS_SELECTOR, tag_set["last_name"]).text
        last_name = full_name.split(' ')[-1]
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



def get_reference_links(driver, tag_set):
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Utilise le tag et la classe CSS spécifiés dans tag_set
        elements = soup.find_all(tag_set["tag"], {'class': tag_set["css_class"]})

        links = []
        for element in elements:
            # Si le tag est 'p', trouver le premier lien à l'intérieur
            if tag_set["tag"] == 'p':
                link = element.find('a')
                if link:
                    url = link.get('href')
            # Si le tag est 'a', utiliser l'élément directement
            elif tag_set["tag"] == 'a':
                url = element.get('href')
            else:
                continue

            # Continuer à traiter l'URL comme auparavant
            if url.startswith("http://doi.org") or url.startswith("https://doi.org") or url.startswith("http://dx.doi.org") or url.startswith("https://dx.doi.org"):
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
        update_into_database(connection, url, None, None, None, -1, False)
        driver.quit()
        return
    tag_set = tags[domain]
    driver.get(url)
    reference_parsed = False  # initialize reference_parsed here
    try:
        title, abstract, content = extract_info(driver, tag_set)
        parsed = 1 if all([title, abstract, content]) else -1
    except Exception as e:
        print(f"An error occurred while extracting data from {url}: {e}")
        title, abstract, content = None, None, None
        parsed = -1
    original_article_id = update_into_database(connection, url, title, abstract, content, parsed, reference_parsed)
    try:
        authors = extract_authors_info(driver, tag_set)
    except Exception as e:
        print(f"An error occurred while extracting authors from {url}: {e}")
        authors = None

    if authors:
        for author in authors:
            first_name, last_name, affiliation, email = author
            author_id = insert_into_authors_database(connection, first_name, last_name, affiliation, email)
            insert_author_article_relation(connection, author_id, original_article_id)

    try:
        reference_links = get_reference_links(driver, tag_set)
        reference_parsed = bool(reference_links)  # update reference_parsed here
    except Exception as e:
        print(f"An error occurred while extracting reference links from {url}: {e}")
        reference_links = []
        reference_parsed = False

    if reference_links:
        insert_reference_links_into_database(connection, original_article_id, reference_links)
        update_reference_extraction_status(connection, original_article_id, True) # Add this line
    else:
        update_reference_extraction_status(connection, original_article_id, False) # Add this line
    
    driver.quit()




# Function to process multiple URLs and extract information
def process_urls(tags, urls, connection):
    for url in urls:  
        process_url(tags, url, connection)


# Function to get URL from database using an ID
def get_url_from_db(connection, id):
    cursor = connection.cursor()
    query = f"SELECT url FROM articles WHERE id = {id};"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result[0][0] if result else None


# Function to check if URL is already in the 'articles' table
def check_url_in_articles(connection, url):
    cursor = connection.cursor()
    query = f"SELECT url FROM articles WHERE url = '{url}';"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return bool(result)

def get_extraction_status(connection, id):
    cursor = connection.cursor()
    query = f"SELECT parsed FROM articles WHERE id = {id};"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


def main():
    connection = create_db_connection()
    tags = load_tags()

    if not os.path.exists('output'):
        os.makedirs('output')

    # Permettre à l'utilisateur de définir un nombre d'heures
    hours = int(input("Combien d'heures souhaitez-vous que le programme s'exécute? "))
    start_time = time.time()

    id = 1
    while True:
        # Vérifiez si le temps écoulé est supérieur au temps défini par l'utilisateur
        elapsed_time = time.time() - start_time
        if elapsed_time > hours * 3600:  # Convertir les heures en secondes
            print("Le temps alloué est écoulé!")
            break

        extraction_status = get_extraction_status(connection, id)

        if extraction_status is None:
            print(f"No record found for ID: {id}")
            id += 1
            continue

        if extraction_status == 0:
            url = get_url_from_db(connection, id)
            if url:
                process_url(tags, url, connection)
            else:
                print(f"URL with ID {id} not found.")
        else:
            print(f"Skipping URL with ID {id} as it has already been processed.")

        id += 1


if __name__ == "__main__":
    main()
