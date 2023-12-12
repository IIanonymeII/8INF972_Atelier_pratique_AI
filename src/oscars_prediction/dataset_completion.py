# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 00:16:11 2023

@author: basil
"""
import API
import pandas as pd

def addMoviesOfGivenYear(year, df):
    data = API.getMostPopularMoviesPerYear(year)
    condition = (df['Year'] == year)
    filtered_values = df.loc[condition, 'Title']
    for movie in data:
        current = data[movie]
        if current["title"] not in filtered_values.values:
            new_element = [current["title"], current["genres"], current["keywords"], year, 0, 0, 0, 0, 0, 0]
            df = pd.concat([df, pd.DataFrame([new_element], columns=df.columns)], ignore_index=True)
    return df