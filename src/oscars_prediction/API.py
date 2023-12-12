# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 03:08:09 2023

@author: basil
"""


import requests
import json

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4OGQ3YmZiN2EyZDgwMjYyM2ZlYzNmOWM3M2Q4MDI0MCIsInN1YiI6IjYwMzQwNmYwNDA4M2IzMDAzZjUzMWQxNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.mdCmwFjph61J40vu6SkqRk2TWNjTvCjJEaZ9PvRAYks"
}

def getMovieID(title, year):
    encoded = requests.utils.quote(title)
    url = "https://api.themoviedb.org/3/search/movie?query=" + encoded + "&include_adult=false&page=1"
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    if data["total_results"] == 0:
        result_id = -1
        print(f"{title}: No results")
    else:
        # Iterate through the "results" list to find the first result with a 2022 release year
        result_id = -1  # Default value if not found
        for result in data["results"]:
            if(result["release_date"] != ""):
                yearJSON = int(result["release_date"].split('-')[0])
                if abs(yearJSON - int(float(year))) <= 2:
                    result_id = result["id"]
                    break  # Exit the loop when the first matching result is found
    return result_id

def getKeywords(ID):
    url = "https://api.themoviedb.org/3/movie/" + str(ID) + "/keywords"
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    keywords = [keyword["name"] for keyword in data["keywords"]]
    return keywords

def getMovieInfo(title, year):
    ID = getMovieID(title, year)
    if ID == -1:
        return ([], [])
    url = "https://api.themoviedb.org/3/movie/" + str(ID)
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    genres_names = [genre["name"] for genre in data["genres"]]
    keywords = getKeywords(ID)
    return (genres_names, keywords)

def getMostPopularMoviesPerYear(year):
    data = {}
    for i in range(1,10):
        url = "https://api.themoviedb.org/3/discover/movie?page=" + str(i) + "&primary_release_year=" + str(year) + "&sort_by=vote_count.desc"
        response = requests.get(url, headers=headers)
        dataMovies = json.loads(response.text)
        for result in dataMovies["results"]:
            ID = result["id"]
            print(ID)
            urlMovie = "https://api.themoviedb.org/3/movie/" + str(ID)
            responseMovie = requests.get(urlMovie, headers=headers)
            movie = json.loads(responseMovie.text)
            title = movie["original_title"]
            genres_names = [genre["name"] for genre in movie["genres"]]
            keywords = getKeywords(ID)
            data[title] = {
                "title": title,
                "genres": genres_names,
                "keywords": keywords,
                "year": year
            }
    return data