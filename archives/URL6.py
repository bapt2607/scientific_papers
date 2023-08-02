import requests
from bs4 import BeautifulSoup

url = 'https://www.sciencedirect.com/science/article/pii/S136184151730155X'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    'From': 'youremail@domain.com'
}

response = requests.get(url, headers=headers)

# Utiliser html5lib pour parser la réponse
soup = BeautifulSoup(response.content, 'html5lib')



# Pour extraire le contenu
try:
    body_element = soup.find(id='body')
    if body_element is not None:
        paragraphs = body_element.find_all('p')
        for p in paragraphs:
            print(p.get_text())
    else:
        print("Element with id='body' not found")
except Exception as e:
    print("Content not found:", e)
