import requests
from lxml import html

url = 'https://www.sciencedirect.com/science/article/pii/S2090123221001491'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    'From': 'youremail@domain.com'
}

response = requests.get(url, headers=headers)
tree = html.fromstring(response.content)

# Pour extraire le titre
try:
    title = tree.xpath('//title/text()')[0]
    print("Title: ", title)
except IndexError:
    print("Title not found")

# Pour extraire le résumé
try:
    abstract = tree.xpath('//div[contains(@class, "abstract author")]/div/p/text()')[0]
    print("Abstract: ", abstract)
except IndexError:
    print("Abstract not found")

# Pour extraire le contenu
try:
    content = tree.xpath('//*[@id="body"]//p//text()')
    print("Content: ", content)
except IndexError:
    print("Content not found")
