import csv
import numpy as np
import requests
from bs4 import BeautifulSoup


def goThroughYear(years):
    return_result = []
    for year in years:
        result = {"year": year, "movies": []}
        urlList = "https://letterboxd.com/films/ajax/popular/year/" + \
            str(year) + "/?esiAllowFilters=true"
        soup = BeautifulSoup(requests.get(urlList).text, 'html.parser')
        movies = soup.find_all('li', {'class': "listitem poster-container"})
        for movie in movies:
            div_movie = movie.find("div")
            link = "https://letterboxd.com" + \
                div_movie.get('data-target-link') + "genres/"
            result["movies"].append(getMovieGenre(link))
        return_result.append(result)
    return return_result


def getMovieGenre(link):
    result = {"name": "?", "genres": [], "themes": []}

    soup = BeautifulSoup(requests.get(link).text, 'html.parser')
    print(soup.find("h1", {'class': "prettify"}).get_text())
    result["name"] = soup.find("h1", {'class': "prettify"}).get_text()
    genres_and_theme_div = soup.find('div', {'id': "tab-genres"})
    sub_genres_and_theme_div = genres_and_theme_div.find_all(
        'div', {"class": "text-sluglist"})
    if (len(sub_genres_and_theme_div) == 2):
        genres = sub_genres_and_theme_div[0].find_all('a')
        themes = sub_genres_and_theme_div[1].find_all('a')
        # print(" == Genres ==")
        # print(genres)
        for genre in genres:
            # print(genre.text.strip())
            result["genres"].append(genre.text.strip())

        # print(" == Themes ==")
        for theme in themes:
            if "Show All…" not in theme.text.strip():
                result["themes"].append(theme.text.strip())
    return result


def save_to_csv(filename, data):
    with open(filename, mode='w', newline='') as file:
        fieldnames = ["year", "name", "genres", "themes"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for year in data:
            for item in year["movies"]:
                # Convert the "genres" and "themes" lists to comma-separated strings
                item["year"] = year["year"]
                item["genres"] = ', '.join(item["genres"])
                item["themes"] = ', '.join(item["themes"])
                print(item)
                writer.writerow(item)


list_date = np.arange(2010, 2023, 1)
print(list_date)

data_to_save = goThroughYear(list_date)


save_to_csv('output.csv', data_to_save)
