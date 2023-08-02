import requests
from bs4 import BeautifulSoup

def get_reference_links(url):
    # Faites une requête GET à l'URL
    response = requests.get(url)

    # Vérifiez si la requête a réussi
    if response.status_code == 200:
        # Analysez le contenu HTML de la page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Trouvez tous les liens <a> dans la page
        all_links = soup.find_all('a')

        # Liste pour stocker les liens des références
        reference_links = []

        # Parcourez les liens et filtrez ceux qui correspondent à vos critères
        for link in all_links:
            # Vérifiez si le lien a une classe ou un attribut spécifique
            if link.get('class') == ['article-title']:
                url = link.get('href')
                reference_links.append(url)

        return reference_links

    else:
        print("La requête a échoué avec le code d'état :", response.status_code)
        return []

# URL de la page à extraire
url = "https://peerj.com/articles/15572/"

# Appel de la fonction pour obtenir les liens des références
references = get_reference_links(url)

# Affichage des liens des références
for reference in references:
    print(reference)
