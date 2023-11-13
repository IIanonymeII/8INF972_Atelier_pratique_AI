#AUTHOR : Diane Lantran
import pandas as pd
import os
import json
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
import chardet
import shutil
import actorPopularityScrap

### DATASETS ###
current_directory = os.getcwd()
# forbes 100 income dataset
file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'forbes_celebrity_100.csv')
forbes_data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',')
file = os.path.join(current_directory, 'src', 'actorsAlgorithm', 'personalities_data.csv')
personalities_data = pd.read_csv(file, encoding='ISO-8859-1', sep=',')

def keep_first_occurrence(data, path):
    # Keep only the first occurrence of each unique name
    forbes_data = data.drop_duplicates(subset='Name', keep='first')

    # Save the modified DataFrame back to the CSV file
    forbes_data.to_csv(path, index=False)

### Scrap and calculate forbes populariy score ###
def scrapPersonality():
    i = 0
    tot_celebrities = len(forbes_data)
    for celebrity in forbes_data['Name']:
        i = i+1
        if not is_celebrity_registered(celebrity):
            print(i, "/", tot_celebrities)
            actorPopularityScrap.scrapActorGoogleTrends(celebrity)
            nb_follow = actorPopularityScrap.scrapActorFollowers(celebrity)
            add_data(celebrity, nb_follow)


def add_data(personality_name, nb_followers):
    if nb_followers and nb_followers.strip():  # Check if it's not empty or contains only whitespace
        nb_followers = int(''.join(filter(str.isdigit, str(nb_followers))))
    else:
        nb_followers = None
    with open('src/actorsAlgorithm/personalities_data.csv', 'a', newline='') as csvfile:
        print("j'enregistre : ", personality_name, "followers : ", nb_followers)

        writer = csv.writer(csvfile)

        # Write the new row
        writer.writerow([personality_name, nb_followers, ''])

def is_celebrity_registered(celebrity_name):
    file_path = 'src/actorsAlgorithm/personalities_data.csv'
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'Name' not in reader.fieldnames:
                print('colonne mal implementée')
                return False

            for row in reader:
                if row['Name'] == celebrity_name:
                    return True
    except FileNotFoundError:
        # Handle the case where the file is not found
        return False
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {e}")
        return False

keep_first_occurrence(forbes_data, file_path)
keep_first_occurrence(personalities_data, file)
scrapPersonality()
