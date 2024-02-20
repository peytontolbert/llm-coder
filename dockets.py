import json
from bs4 import BeautifulSoup

# List of files to parse
files_to_parse=['dockets.txt']

# List to hold all extracted data
all_data = []


# Iterate over each file and parse the HTML content
for filename in files_to_parse:
    with open(filename, 'r') as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all the rows in the table
    rows = soup.find_all('tr', {'role': 'row'})

    # Iterate over each row and extract the required information
    for row in rows:
        docket_td = row.find('td', {'aria-describedby': 'results-table_DocketNumber'})
        document_name_td = row.find('td', {'aria-describedby': 'results-table_Description'})
        link_td = document_name_td.find('a', {'class': 'link'}) if document_name_td else None

        # Extract the information if the 'td' elements are found
        docket_number = docket_td.get_text(strip=True).replace('Docket #', '').strip() if docket_td else None
        document_name = document_name_td.get_text(strip=True).replace('Document Name', '').strip() if document_name_td else None
        link = link_td.get('href') if link_td else None

        # Create a dictionary with the extracted information
        data = {
            'Docket Number': docket_number,
            'Document Name': document_name,
            'Link': link
        }

        # Add the dictionary to the list of all data
        all_data.append(data)

# Save the extracted data to a JSON file
with open('extracted_dockets.json', 'w') as json_file:
    json.dump(all_data, json_file, indent=4)

print(f"Data extracted and saved to 'extracted_data.json'")