import requests
from bs4 import BeautifulSoup

def goThroughYear(year):
    urlList = "https://letterboxd.com/films/ajax/popular/year/" + str(year) + "/?esiAllowFilters=true"
    soup = BeautifulSoup(requests.get(urlList).text, 'html.parser')
    movies = soup.find_all('li', {'class': "listitem poster-container"})
    for movie in movies:
        div_movie = movie.find("div")
        link = "https://letterboxd.com" + div_movie.get('data-target-link') + "genres/"
        getMovieGenre(link)

def getMovieGenre(link):
    soup = BeautifulSoup(requests.get(link).text, 'html.parser')
    genres_div = soup.find('div', {'id': "tab-genres"})
    sub_genres_div = genres_div.find_all('div')
    if (len(sub_genres_div) == 2):
        genres = sub_genres_div[1].find_all('a')
        for genre in genres:
            print(genre.text.strip())
    

goThroughYear(2021)