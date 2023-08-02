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

try:
    abstract = soup.find('span', class_='anchor-text')  # This class or ID will depend on the actual webpage
    abstract.decompose()
except Exception as e:
    print("Abstract not found:", e)

try:
    abstract = soup.find('div', {'class': 'abstract graphical'})  # This class or ID will depend on the actual webpage
    abstract.decompose()
except Exception as e:
    print("Abstract not found:", e)


# Try to exclude the abstract
try:
    abstract = soup.find('div', {'class': 'abstract author'})  # This class or ID will depend on the actual webpage
    abstract.decompose()
except Exception as e:
    print("Abstract not found:", e)

# Pour exclure le footer
try:
    footer = soup.find('footer')
    footer.decompose()
except Exception as e:
    print("Footer not found:", e)

# Pour extraire le contenu
try:
    content = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'])
    for p in content:
        print(p.get_text(),"\n")
except Exception as e:
    print("Content not found:", e)