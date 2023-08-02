
# Check if the request was successful
if response.status_code == 200:
  # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the text content from the modified HTML
    section_introduction = soup.find('div', {'id': 'preview-section-introduction'}).text.strip()

    # Display the text
    print("Text from the Web Page section_introduction\n")
    print(section_introduction,"\n")
else:
    print("The request failed with code:", response.status_code)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the text content from the modified HTML
    section_snippets = soup.find('div', {'id': 'preview-section-snippets'}).text.strip()

    # Display the text
    print("Text from the Web Page section_snippets:\n")
    print(section_snippets,"\n")
else:
    print("The request failed with code:", response.status_code)
