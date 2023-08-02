from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration du webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Définir l'URL de l'article
url = "https://www.sciencedirect.com/science/article/pii/S2589537021001541"

# Charger la page web
driver.get(url)

# Extraire le titre
title = driver.find_element(By.CSS_SELECTOR,'span.title-text').text

# Extraire le résumé
abstract = driver.find_element(By.CSS_SELECTOR, '.abstract.author').text

# Attendre que le texte de l'élément change de 'Loading...'
WebDriverWait(driver, 30).until_not(
    EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'div.Body.u-font-gulliver.text-s#body'), 'Loading...')
)

# Réobtenir l'élément du contenu principal et extraire le texte
content = driver.find_element(By.CSS_SELECTOR, 'div.Body.u-font-gulliver.text-s#body').text

print("Titre :", title)
print("Résumé :", abstract)
print("Contenu :", content)

# Fermer le navigateur
driver.quit()
