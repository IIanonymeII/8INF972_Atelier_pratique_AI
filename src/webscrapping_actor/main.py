import csv
import requests
from bs4 import BeautifulSoup

import re


def extract_year(input_string):
    # This pattern looks for four consecutive digits (the year)
    pattern = r'\d{4}'

    match = re.search(pattern, input_string)

    if match:
        year = match.group()
        return year
    else:
        return None  # Return None if the year is not found in the string


def scrape_film_page(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        # If there is a network problem (e.g. DNS resolution, refused connection, etc), print the error and return an empty list
        print(f"An error occurred: {e}")
        return []

    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the infobox with the film details
    infobox = soup.find('table', {'class': 'infobox'})

    actors = []

    # Check if the infobox exists
    if infobox:
        for infobox_part in infobox:
            # Check if the row contains the 'Starring' field
            if "Starring" in str(infobox_part):
                for starring in infobox_part:
                    # Check if the cell contains the 'Starring' field
                    if "Starring" in str(starring):
                        # Find all links in the cell (each link corresponds to an actor)
                        for link in starring.find_all("a"):
                            # Extract the actor's name from the link text and add it to the list
                            actor = link.text.strip()
                            actors.append(actor)

    return actors


def scrape_country_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table with the list of number one films
    table = soup.find('table', {'class': 'wikitable'})

    films = []

    if table:
        # Find all rows in the table
        rows = table.find_all('tr')

        for row in rows:
            # Find all columns in the row
            cols = row.find_all('td')
            # print(cols)
            # 0 : rank
            # 1 : date
            # 2 : movies name
            # 3 : gross
            # 4 : Notes

            if cols and len(cols) == 5:
                # The film title is in the first column
                film_title_col = cols[2]

                # The link to the film's page is in the film title column
                link = film_title_col.find(name='a', href=True)
                film_name = film_title_col.text.strip()
                # print(film_name)

                if link:
                    film_url = "https://en.wikipedia.org" + link['href']
                    # Scrape the film page for the list of starring actors
                    actors = scrape_film_page(film_url)

                    films.append((film_name, actors))

    return films


def scrape_wiki(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    data = []

    # Find all tables in the webpage
    tables = soup.find_all('table', {'class': 'wikitable'})

    for table in tables:
        # Find all rows in the table
        rows = table.find_all('tr')

        for row in rows:
            # Find all columns in the row
            cols = row.find_all('td')

            if cols:
                # The country name is in the first column
                country = cols[0].text.strip()

                # The link to the country's box office number one films is in the second column
                link = cols[0].find('a', href=True)
                if link:
                    country_url = "https://en.wikipedia.org" + link['href']
                    year = extract_year(country_url)
                    print(f"{year} - {country}")

                    if 2019 < int(year) < 2021:  # just for test
                        # Scrape the country page for the list of number one films
                        films = scrape_country_page(country_url)
                        data.append([year, country, films])

    return data


def convert_data(list):
    result = []

    for country_list in list:
        if len(country_list) == 3:
            year = country_list[0]
            country = country_list[1]

            for film_list in country_list[2]:
                if len(film_list) == 2:
                    film_name = film_list[0]
                    film_name = re.sub(r'\([0-9]+\)', '', film_name)

                    for actor in film_list[1]:
                        result.append([year, country, film_name, actor])
                else:
                    print(f"ERROR in film_list : {film_list}")
        else:
            print(f"ERROR in country_list : {country_list}")
    return result


def remove_dupliated(list):
    result = []
    for t in list:
        exist = False
        for r in result:
            # == t ==
            # 2 film name
            # 3 actor name

            # == r ==
            # 1 film name
            # 2 actor name
            if (t[2] == r[1]) and (t[3] == r[2]):
                exist = True

        if not exist:
            result.append([t[0], t[2], t[3]])
    return result


def write_csv(data, filename):
    """Writes a list of data to a CSV file.

    Args:
      data: A list of lists or tuples.
      filename: The name of the CSV file to write to.
    """

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for row in data:
            print(row)
            writer.writerow(row)


url = "https://en.wikipedia.org/wiki/Lists_of_box_office_number-one_films"
data = scrape_wiki(url)

result = remove_dupliated(list=convert_data(list=data))

write_csv(data=result, filename="test.csv")
