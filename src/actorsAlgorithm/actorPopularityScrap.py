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

#insta_account = 'odysseyscrapping@gmail.com'
#mdp : 'scrappingwithodyssey'
insta_account = 'odyssey_PMC'
mdp = "instapassOdyssey"


### SCRAPPING UTILS ###
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
def create_driver():
    firefox_options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(service=FirefoxService(executable_path=GeckoDriverManager().install()), options=firefox_options)
    return driver
driver = create_driver()
def waitForOneElement(driver, by, name):
    try:
        return WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)\
                            .   until(EC.presence_of_element_located((by, name)))
    except TimeoutException:
        return None

def get_download_folder():
    home_directory = os.path.expanduser("~")
    download_folder = os.path.join(home_directory, "Downloads")
    return download_folder

### DATASETS ###
# movie dataset
current_directory = os.getcwd()
file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'tmdb_5000_movies.csv')
movie_data = pd.read_csv(file_path)
# credit dataset
file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'tmdb_5000_credits.csv')
credits_data = pd.read_csv(file_path)
# actor dataset
file_path = os.path.join(current_directory, 'src', 'webscrapping_actor', 'actor.csv')
imdb_popularity_data = pd.read_csv(file_path, header=None, names=['Year', 'Title', 'Actor'])

###SETS CONSTANTS ###
default_download = get_download_folder()

# Load existing data from CSV if it exists, otherwise create a new DataFrame
try:
    with open('src/actorsAlgorithm/popularity_data.csv', 'rb') as f:
        result = chardet.detect(f.read())  # or readline if the file is large
    pd.read_csv('src/actorsAlgorithm/popularity_data.csv', encoding=result['encoding'])
except FileNotFoundError:
    popularity_data = pd.DataFrame(columns=['Actor', 'Followers', 'Is_In_IMDB', 'Score'])


# Cree un dataset permettant de calculer le score de popularité de chaque acteur suivant le genre du film
def createPopularityDataSet():
    movies = known_cast_movies()
    i = 0
    for movie in movies:
        print("film : ", i, "/", len(movies))
        if i>3:
            fillPopularityDataSet(movie)
        i += 1
    

def get_cast(my_movie):
    # Iterate over rows in the DataFrame
    for index, row in credits_data.iterrows():
        current_title = row['title']
        cast_json = row['cast']  # Assuming 'cast' is a column in your DataFrame

        if current_title == my_movie:
            cast_list = json.loads(cast_json)
            cast_names = [cast_member["name"] for cast_member in cast_list]
            return cast_names



def fillPopularityDataSet(my_movie):
    print("film traité : ", my_movie)
    #fills the dataset used to calculate the popularity score of an actor
    j = 0 #counts the number of actors treated
    cast = get_cast(my_movie)
    for cast_member in cast:
        print("actor : ", j, "/", len(cast))
        pop = 0
        # si le nom est dans actor.csv il est populaire d apres imdb
        if cast_member in imdb_popularity_data['Actor']:
            pop = 1
        

        if not is_actor_registered('src/actorsAlgorithm/popularity_data.csv', cast_member):
            print(cast_member)
            scrapActorGoogleTrends(cast_member)
            nb_follow = scrapActorFollowers(cast_member)
            add_data(cast_member, nb_follow, pop)
        j+=1         

def add_data(actor_name, nb_followers, is_in_IMDB):
    if nb_followers and nb_followers.strip():  # Check if it's not empty or contains only whitespace
        nb_followers = int(''.join(filter(str.isdigit, str(nb_followers))))
    else:
        nb_followers = None
    with open('src/actorsAlgorithm/popularity_data.csv', 'a', newline='') as csvfile:
        print("j'enregistre : ", actor_name, "followers : ", nb_followers)

        writer = csv.writer(csvfile)

        # Write the new row
        writer.writerow([actor_name, nb_followers, is_in_IMDB, ''])

def is_actor_registered(file_path, actor_name):
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'Actor' not in reader.fieldnames:
                print('colonne mal implementée')
                return False

            for row in reader:
                if row['Actor'] == actor_name:
                    return True
    except FileNotFoundError:
        # Handle the case where the file is not found
        return False
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {e}")
        return False

    return False

def scrapActorFollowers(username):
        success = False
        attempts = 0
        followers_count = None
        while((attempts < 2) and (success == False) ):
            driver.get('https://www.google.ca/?hl=fr')
            try:
                #teste si le pop up cookies est displayed, si oui click refuser
                button = waitForOneElement(driver, By.ID, 'W0wltc')
                if button is not None and button.is_displayed():
                    button.click()


                search_box = waitForOneElement(driver, By.NAME, 'q')
                if search_box:
                    search_box.send_keys(f'{username} on Instagram')
                    search_box.submit()
                    #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[jsname="UWckNb"][href*="instagram.com"]'))).click()
                    first_result = waitForOneElement(driver, By.CSS_SELECTOR, 'a[jsname="UWckNb"][href*="instagram.com"]')
                    if first_result:
                        first_result.click()

                        # refus des cookies
                        button = waitForOneElement(driver, By.CLASS_NAME, '_a9--')
                        if button is not None and button.is_displayed():
                            button.click() 
                        
                        # #connection to instagram
                        # account = waitForOneElement(driver, By.NAME, 'username')
                        # if account is not None and account.is_displayed() :
                        #     account.clear()
                        #     account.send_keys(insta_account)
                        # mdp_area = waitForOneElement(driver, By.NAME, 'password')
                        # if mdp_area is not None and mdp_area.is_displayed() : 
                        #     mdp_area.clear()
                        #     mdp_area.send_keys(mdp)
                        #     mdp_area.send_keys(Keys.RETURN)
                        
                        #get the number of followers of the actor
                        followers_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="_ac2a" and @title][1]')))
                        if followers_element:
                            followers_count = followers_element.get_attribute('title')
                            print("nb followers : ", followers_count)
                            success = True
                break                    
            except StaleElementReferenceException:
                print("StaleElementReferenceException, ", username)
                time.sleep(2)
                attempts += 1
            except TimeoutException:
                print(f"TimeoutException while scraping followers for {username}")
                time.sleep(2)
                attempts += 1
        return(followers_count)

def scrapActorGoogleTrends(username):
        success = False
        attempts = 0
        while((attempts < 4) and (success == False) ):
            driver.get('https://trends.google.fr/trends?geo=US&hl=fr')
            try:
                search_box = waitForOneElement(driver, By.ID, 'i7') #access the google trends search box
                if search_box:
                    search_box.clear()
                    search_box.send_keys(f'{username}')
                    search_box.send_keys(Keys.RETURN)
                    
                    #selects "12 derniers mois" in Time period picker
                    time_period_picker = waitForOneElement(driver, By.ID, 'select_10')
                    if time_period_picker and time_period_picker.is_enabled():
                        time_period_picker.click()  # Click to open the dropdown
                        # Wait for the dropdown menu to be present
                        dropdown_menu = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, 'select_container_11'))
                        )

                        options = dropdown_menu.find_elements(By.CLASS_NAME, 'custom-date-picker-select-option')
                        for option in options:
                            if option.text == '12 derniers mois':
                                option.click()
                                break

                    #downloads the corresponding .csv file as : {username}_trend.csv
                    download_button = waitForOneElement(driver, By.CSS_SELECTOR, 'button.export')
                    if download_button and download_button.is_enabled():
                        driver.execute_script("arguments[0].click();", download_button)
                        print("downloading")
                        time.sleep(2)  # Wait for the file to download
                        src_path = os.path.join(default_download,'multiTimeline.csv')
                        dest_path = os.path.join("src","actor_trends_scrap", f"{username}_trend.csv")
                        if os.path.exists(src_path):
                            if os.path.exists(dest_path):
                                os.replace(src_path, dest_path)
                            else:
                                shutil.move(src_path, dest_path)

                            # Set success to True since the operation completed
                            success = True
                    attempts +=1

            except StaleElementReferenceException:
                print("StaleElementReferenceException, ", username)
                time.sleep(2)
                attempts += 1  

#Tests : 
def known_cast_movies():
    known_cast_movies = []  # Initialize an empty list to store movie titles
    for i in range(credits_data.shape[0]):
        movie_title = credits_data.loc[i, 'title']
        known_cast_movies.append(movie_title)
    return known_cast_movies

#createPopularityDataSet()
#driver.quit() # Close the browser