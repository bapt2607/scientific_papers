from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configuration du navigateur Selenium avec WebDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Chargement de la page
url = "https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.14919"
driver.get(url)

# Fermez le bandeau de consentement des cookies
try:
    cookie_banner = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.osano-cm-accept-all')))
    cookie_banner.click()
except TimeoutException:
    print("Le bandeau de consentement des cookies n'a pas été trouvé sur la page.")

# Trouver le bouton et cliquer dessus
try:
    button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'accordion__control')]")))
    ActionChains(driver).move_to_element(button).perform()  # Faites défiler la page jusqu'au bouton
    driver.execute_script("document.getElementsByClassName('accordion__control')[0].click();")
    driver.get_screenshot_as_file("screenshot_after_click.png")  # Faire une capture d'écran après le clic
except TimeoutException:
    print("Le bouton n'a pas été trouvé sur la page.")

# Imprimer le contenu du div qui apparaît après avoir cliqué sur le bouton
try:
    div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "accordion__content")))
    print(div.text)
except TimeoutException:
    print("Le div n'a pas été trouvé sur la page.")

driver.quit()

