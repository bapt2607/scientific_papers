from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Configuration du navigateur Selenium avec WebDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Chargement de la page
url = "https://peerj.com/articles/15572/"
driver.get(url)
#<section class="ref-list-container" id="references">
# Attente explicite jusqu'à ce que l'élément masqué soit présent dans le DOM
wait = WebDriverWait(driver, 10)
try:
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ref-list-container')))
except TimeoutException:
    print("L'élément CSS n'a pas été trouvé sur la page.")
    driver.quit()
    exit()
#<div tabindex="0" role="button" class="accordion__control" aria-controls="idcgf14919-bibl-0001" aria-expanded="false" data-references="/action/ajaxShowEnhancedAbstract?widgetId=cea03f16-41db-4f4d-9961-d720aa41d028&ajax=true&doi=10.1111%2Fcgf.14919&pbContext=%3Bpage%3Astring%3AArticle%2FChapter+View%3Bctype%3Astring%3AJournal+Content%3Bwebsite%3Awebsite%3Apericles%3Barticle%3Aarticle%3Adoi%5C%3A10.1111%2Fcgf.14919%3BsubPage%3Astring%3AAccess+Denial%3Bjournal%3Ajournal%3A14678659%3Bwgroup%3Astring%3APublication+Websites%3BrequestedJournal%3Ajournal%3A14678659%3BpageGroup%3Astring%3APublication+Pages%3Bcsubtype%3Astring%3AAhead+of+Print&onlyLog=true">…</div>flex
# Trouver tous les liens à partir de l'élément
links = element.find_elements(By.TAG_NAME, 'a')

# Afficher les URL des liens
if len(links) > 0:
    for link in links:
        href = link.get_attribute('href')
        print(href)
else:
    print("Aucun lien trouvé dans l'élément masqué.")

# Fermeture du navigateur
driver.quit()
