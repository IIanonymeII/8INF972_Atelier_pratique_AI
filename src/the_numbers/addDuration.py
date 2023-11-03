
import requests
import pandas as pd
import json
FIRST_YEAR = 1970
LAST_YEAR = 2021
COL_NAMES = ["Title", "Year", "Month", "MPAA Rating", "Original domestic B.O",
             "Original international B.O", "Adjusted domestic B.O",
             "Adjusted international B.O","Original budget","Adjusted budget",
             "Duration", "Keywords", "Source", "Production method", 
             "Creative type", "Companies", "Countries", "Languages", "Genres"]

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

def getMovieInfo(ID):
    url = "https://api.themoviedb.org/3/movie/" + str(ID)
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    runtime = data["runtime"]
    return (runtime)


for year in range(FIRST_YEAR, LAST_YEAR + 1, 1):
    print(year)
    df = pd.read_csv('movies' + str(year) + '.csv')
    for index, row in df.iterrows():
        if (pd.isna(row["Duration"])):
            title = row["Title"]
            ID = getMovieID(title, year)
            if ID != -1:
                runtime = getMovieInfo(ID)
                df.at[index, "Duration"] = int(runtime)
                print(f"{title} ({year}): new duration: {runtime}")
            
    df.to_csv('movies' + str(year) + '.csv', index=False)