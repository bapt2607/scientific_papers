import requests
from bs4 import BeautifulSoup

url = "https://www.sciencedirect.com/science/article/pii/S2090123221001491"

# Set a custom User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Make the HTTP GET request to the URL using the custom header
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Retrieve the article title (usually found within the <title> tag in the <head> section)
    title = soup.head.title.text

    # Display the title
    print("Article Title:\n")
    print(title,"\n")
else:
    print("The request failed with code:", response.status_code)
print("")
# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Retrieve the article abstract (div tag with a specific class)
    abstract = soup.find('div', {'class': 'abstract author'}).text.strip()

    # Display the abstract
    print("Article Abstract:\n")
    print(abstract,"\n")
else:
    print("The request failed with code:", response.status_code)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Retrieve the article abstract (div tag with a specific class)
    article = soup.find('div', {'class': 'Article'}).text.strip()

    # Display the abstract
    print("Article Abstract:\n")
    print(article,"\n")
else:
    print("The request failed with code:", response.status_code)

