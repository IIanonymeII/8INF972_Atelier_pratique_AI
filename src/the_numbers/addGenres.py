
import requests
import pandas as pd
import json
import os
FIRST_YEAR = 1930
LAST_YEAR = 2022
COL_NAMES = ["Title", "Year", "Month", "MPAA Rating", "Original domestic B.O",
             "Original international B.O", "Adjusted domestic B.O",
             "Adjusted international B.O","Original budget","Adjusted budget",
             "Duration", "Keywords", "Source", "Production method", 
             "Creative type", "Companies", "Countries", "Languages", "Genres"]

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4OGQ3YmZiN2EyZDgwMjYyM2ZlYzNmOWM3M2Q4MDI0MCIsInN1YiI6IjYwMzQwNmYwNDA4M2IzMDAzZjUzMWQxNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.mdCmwFjph61J40vu6SkqRk2TWNjTvCjJEaZ9PvRAYks"
}

def getMovieID(title, year, yearEmpty):
    encoded = requests.utils.quote(title)
    url = "https://api.themoviedb.org/3/search/movie?query=" + encoded + "&include_adult=false&page=1"
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    release_month = release_year = None
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
                    if (yearEmpty):
                        release_year = yearJSON
                        release_month = int(result["release_date"].split('-')[1])
                    break  # Exit the loop when the first matching result is found
    return result_id, release_year, release_month

def getMovieInfo(ID):
    url = "https://api.themoviedb.org/3/movie/" + str(ID)
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    genres_names = [genre["name"] for genre in data["genres"]]
    budget = data["budget"]
    revenue = data["revenue"]
    return (genres_names, budget, revenue)


for year in range(FIRST_YEAR, LAST_YEAR + 1, 1):
    print(year)
    df =pd.read_csv('src/the_numbers/movies' + str(year) + '.csv', names = COL_NAMES)
    new_column_values = []
    inflationRate = None
    for index, row in df.iterrows():
        if (inflationRate == None) and (row["Original domestic B.O"] != None):
            inflationRate = row["Adjusted domestic B.O"] / row["Original domestic B.O"]
        title = row["Title"]
        ID, release_year, release_month = getMovieID(title, year, pd.isna(row["Year"]))
        if release_year != None:
            df.at[index, "Year"] = release_year
            df.at[index, "Month"] = release_month
        if ID != -1:
            data = getMovieInfo(ID)
            if (row["Original domestic B.O"] == None) and (data[2] > 0):
                print(f"{title} ({year}): new BO: {data[2]}")
                df.at[index, "Original domestic B.O"] = int(data[2])
            if (row["Original budget"] == None) and (data[1] > 0):
                print(f"{title} ({year}): new budget: {data[1]}")
                df.at[index, "Original budget"] = int(data[1])
            new_column_values.append(data[0])
            # print(f"{title}: genres: {data[0]}")
        else:
            new_column_values.append([])
    df['Genres'] = new_column_values
    df.drop('Genre', axis=1, inplace=True)  # 'axis=1' specifies that we are removing a column
    os.rename('src/the_numbers/movies' + str(year) + '.csv', 'src/the_numbers/movies' + str(year) + '_old.csv')
    df.to_csv('src/the_numbers/movies' + str(year) + '.csv', index=False)