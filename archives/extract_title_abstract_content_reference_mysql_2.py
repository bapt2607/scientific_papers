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

def create_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Remplacez par le nom de votre hôte si différent
            user="root",  # Remplacez par votre nom d'utilisateur MySQL si différent
            passwd="Wilson&B@pt26",  # Remplacez par votre mot de passe MySQL
            database="database_name"  # Remplacez par le nom de votre base de données
        )
        print("MySQL Database connection successful")
    except Exception as err:
        print(f"Error: '{err}'")

    return connection


def insert_into_database(connection, url, title, abstract, content):
    cursor = connection.cursor()
    query = """
    INSERT INTO articles (url, title, abstract, content) VALUES (%s, %s, %s, %s)
    """
    values = (url, title, abstract, content)
    try:
        cursor.execute(query, values)
        connection.commit()
        print("Data inserted successfully")
    except Exception as err:
        print(f"Error: '{err}'")

def insert_links_into_database(connection, url, references):
    cursor = connection.cursor()
    query = """
    INSERT INTO links (article_url, reference_url) VALUES (%s, %s)
    """
    for link in references:
        values = (url, link)
        try:
            cursor.execute(query, values)
            connection.commit()
            print("Link inserted successfully")
        except Exception as err:
            print(f"Error: '{err}'")

def load_tags():
    with open('tags.json', 'r') as f:
        tags = json.load(f)
    return tags

def setup_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver

def extract_title(driver, tag_set):
    try:
        title = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["title"]))
        ).text
        return title
    except Exception:
        print("Failed to extract title from the page.")
        return None

def extract_abstract(driver, tag_set):
    try:
        abstract = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, tag_set["abstract"]))
        ).text
        return abstract
    except Exception:
        print("Failed to extract abstract from the page.")
        return None

def extract_content(driver, tag_set):
    try:
        WebDriverWait(driver, 60).until_not(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, tag_set["content"]), "Loading...")
        )
        content = driver.find_element(By.CSS_SELECTOR, tag_set["content"]).text
        return content
    except Exception as e:
        print(f"Failed to extract content from the page due to {str(e)}.")
        return None

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

            links.append(url)
        return links
    except Exception as e:
        print(f"Failed to extract reference links from the page. Error: {e}")
        return None

def extract_info(driver, tag_set):
    title = extract_title(driver, tag_set)
    abstract = extract_abstract(driver, tag_set)
    content = extract_content(driver, tag_set)
    return title, abstract, content

def process_url(tags, url, connection):
    driver = setup_driver()
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
    driver.get(url)
    try:
        title, abstract, content = extract_info(driver, tag_set)
        references = get_reference_links(driver, tag_set)
        insert_into_database(connection, url, title, abstract, content)
        insert_links_into_database(connection, url, references)
    except Exception as e:
        print(f"An error occurred while extracting data from {url}: {e}")
    driver.quit()

def process_urls(tags, urls, connection):
    for url in urls:  
        process_url(tags, url, connection)




def get_urls_from_db(connection):
    cursor = connection.cursor()
    query = "SELECT reference_url FROM links;"
    cursor.execute(query)
    result = cursor.fetchall()  # Récupère tous les enregistrements de la requête
    return [url[0] for url in result]  # Extrayez les URLs de la liste des tuples

def main():

    connection = create_db_connection()  # Créez la connexion ici
    tags = load_tags()
    urls = get_urls_from_db(connection)  # Obtenez les URLs de la base de données

    if not os.path.exists('output'):
        os.makedirs('output')
    process_urls(tags, urls, connection)  # Passez la connexion ici


if __name__ == "__main__":
    main()