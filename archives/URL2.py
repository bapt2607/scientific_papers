import requests
from bs4 import BeautifulSoup

# L'URL de l'article
url = "https://www.sciencedirect.com/science/article/pii/S136184151730155X"

# Envoyer une demande GET à l'URL
response = requests.get(url)

# Analyser le contenu de la page avec BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Extraire le titre, le résumé et le contenu de l'article
# Note : Les sélecteurs CSS utilisés ici sont hypothétiques et peuvent ne pas fonctionner sur le site web réel
title_element = soup.select_one('span.title-text')
if title_element is not None:
    title = title_element.text
else:
    title = "Title not found"

print("Title: ", title)