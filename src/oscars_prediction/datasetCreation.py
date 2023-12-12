# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 00:16:11 2023

@author: basil
"""

import pandas as pd
import re
import API
from dataset_completion import addMoviesOfGivenYear
import ast
from sklearn.preprocessing import MultiLabelBinarizer
oscars = pd.read_csv(r'../../data/oscars.csv')
new_df = pd.DataFrame(columns = ["Title", "Genres", "Keywords", "Year"])


new_df[["Main_nominations", "Technical_nominations", "Artistic_nominations",
        "Main_winner", "Technical_winner", "Artistic_winner"]] = 0
oscars.dropna(inplace = True)
for index, row in oscars.iterrows():
    category = row["category"]
    if "SHORT" in category:
        continue
    col = None
    if re.match(r'^(ACTOR|ACTRESS|DIRECTING.*|WRITING.*|BEST PICTURE|BEST MOTION PICTURE|OUTSTANDING PICTURE)', 
                category):
        col = "Main"
        oscars = oscars
    elif re.match(r'^(CINEMATOGRAPHY|SOUND RECORDING|FILM EDITING|SPECIAL EFFECTS|SOUND.*|VISUAL EFFECTS|SPECIAL VISUAL EFFECTS|ENGINEERING EFFECTS)', 
                  category):
        col = "Technical"
    elif re.match(r'^(COSTUME DESIGN.*|MUSIC.*|MAKEUP.*|PRODUCTION DESIGN|ART DIRECTION|DANCE DIRECTION)', 
                  category):
        col = "Artistic"
        
        
    if col != None:
        existing_index = new_df[(new_df['Title'] == row["film"]) & (new_df['Year'] == row["year_film"])].index
        if existing_index.empty:
            genres, keywords = API.getMovieInfo(row['film'], row["year_film"])
            new_element = [row["film"], genres, keywords, row["year_film"], 0, 0, 0, 0, 0, 0]
            new_df = pd.concat([new_df, pd.DataFrame([new_element], columns=new_df.columns)], ignore_index=True)
            existing_index = new_df.index[-1]
        else:
            existing_index = existing_index[0]
        new_df.at[existing_index, col + "_nominations"] += 1
        if row["winner"] == True:
            new_df.at[existing_index, col + "_winner"] += 1

for year in range(1993,2023):
    new_df = addMoviesOfGivenYear(year, new_df)

new_df['Genres'] = new_df['Genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
mlb = MultiLabelBinarizer()
new_df = new_df.join(pd.DataFrame(mlb.fit_transform(new_df['Genres']),columns=mlb.classes_))
new_df.to_csv((r'../../data/oscars_with_genres.csv'), index=False)