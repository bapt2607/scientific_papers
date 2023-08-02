import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_reference_links(url, css_class):
    # Configurez Selenium pour utiliser Chrome
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service)

    # Accédez à la page Web avec Selenium
    driver.get(url)

    # Laissez le navigateur charger la page
    time.sleep(5)

    # Obtenez le contenu de la page avec Selenium
    html = driver.page_source

    # Utilisez BeautifulSoup pour analyser le HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Trouvez tous les liens <a> dans la page avec la classe spécifique
    reference_links = soup.find_all('a', {'class': css_class})

    # Liste pour stocker les liens des références
    links = []

    # Parcourez les liens et obtenez les URLs
    for link in reference_links:
        url = link.get('href')
        links.append(url)

    # Fermez le navigateur
    driver.quit()

    return links

# Lire le fichier de configuration JSON
with open('config.json') as f:
    config = json.load(f)
css_class = config["css_class"]

# URL de la page à extraire
url = "https://peerj.com/articles/15572/"

# Appel de la fonction pour obtenir les liens des références
references = get_reference_links(url, css_class)

# Affichage des liens des références
for reference in references:
    print(reference)
