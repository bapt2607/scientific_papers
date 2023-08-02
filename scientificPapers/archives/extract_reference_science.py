import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_reference_links(url):
    # Configurez Selenium pour utiliser Chrome
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service)

    # Accédez à la page Web avec Selenium
    driver.get(url)

    # Laissez le navigateur charger la page (selon le site, vous pourriez avoir besoin d'un délai plus long)
    time.sleep(5)

    # Obtenez le contenu de la page avec Selenium
    html = driver.page_source

    # Utilisez BeautifulSoup pour analyser le HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Trouvez tous les liens <a> dans la page avec la classe spécifique
    reference_links = soup.find_all('a', {'class': 'anchor link anchor-default'})

    # Liste pour stocker les liens des références
    links = []

    # Parcourez les liens et obtenez les URLs
    for link in reference_links:
        url = link.get('href')
        links.append(url)

    # Fermez le navigateur
    driver.quit()

    return links

# URL de la page à extraire
url = "https://www.sciencedirect.com/science/article/pii/S221267161400105X"

# Appel de la fonction pour obtenir les liens des références
references = get_reference_links(url)

# Affichage des liens des références
for reference in references:
    print(reference,"\n")
