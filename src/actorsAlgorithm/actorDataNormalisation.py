#AUTHOR : Diane Lantran
import os
import pandas as pd
import numpy as np
import pandas as pd
from io import StringIO
from datetime import datetime
import chardet



### INSTAGRAM WEBSCRAPPING DATAS ###
current_directory = os.getcwd()
trend_scrapped_folder = os.path.join(current_directory, 'src', 'actor_trends_scrap')
treated_data_folder = os.path.join(current_directory, 'src', 'actor_trends_treated')

import os
import pandas as pd

with open('src/actor_trends_scrap/Aaron James Cash_trend.csv', 'rb') as f:
    result = chardet.detect(f.read())


def process_trend_files():
    n = len(os.listdir(trend_scrapped_folder))
    i = 0
    for filename in os.listdir(trend_scrapped_folder):
        print(i,"/",n)
        file_path = os.path.join(trend_scrapped_folder, filename)
        save_path = os.path.join(treated_data_folder, filename)
        try:
            df = pd.read_csv(file_path, skiprows=2, encoding=result['encoding'])
            if not df.iloc[:, 1].dropna().empty:
                df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors='coerce').fillna(0) #replace the non float values by 0
                df.rename(columns={df.columns[1]: 'Value'}, inplace=True)
                df = df[::-1]
                df.reset_index(drop=True, inplace=True)
                df.to_csv(save_path, index=False)
            else :
                actor_name = df.columns[1].split(":")[0].strip()
                #deleteCelebrityPopularityRecord(actor_name)
                deleteActorPopularityRecord(actor_name)
        except Exception as e:

            print(f"An error occurred processing {filename}: {str(e)}")
        i = i+1

def cleanNoFollowersData():
    with open('src/actorsAlgorithm/popularity_data.csv', 'rb') as f:
        result = chardet.detect(f.read())  # or readline if the file is large
    popularity_data = pd.read_csv('src/actorsAlgorithm/popularity_data.csv', encoding=result['encoding'])
    for index, row in popularity_data.iterrows():
        actor_name = row['Actor']
        followers = row['Followers']
        if pd.isna(followers):
            print('I delete ', actor_name)
            deleteActorPopularityRecord(actor_name)
            popularity_data = pd.read_csv('src/actorsAlgorithm/popularity_data.csv', encoding=result['encoding'])


def deleteActorPopularityRecord(actor_name):
    with open('src/actorsAlgorithm/popularity_data.csv', 'rb') as f:
        result = chardet.detect(f.read())  # or readline if the file is large
    popularity_data = pd.read_csv('src/actorsAlgorithm/popularity_data.csv', encoding=result['encoding'])
    popularity_data = popularity_data[popularity_data['Actor'] != actor_name]
    popularity_data.to_csv('src/actorsAlgorithm/popularity_data.csv', index=False)

def deleteCelebrityPopularityRecord(actor_name):
    with open('src/actorsAlgorithm/personalities_data.csv', 'rb') as f:
        result = chardet.detect(f.read())  # or readline if the file is large
    personalities_data = pd.read_csv('src/actorsAlgorithm/personalities_data.csv', encoding=result['encoding'])
    personalities_data = personalities_data[personalities_data['Name'] != actor_name]
    personalities_data.to_csv('src/actorsAlgorithm/popularity_data.csv', index=False)

def cleanActorDataSet():
    process_trend_files()
    cleanNoFollowersData()



    