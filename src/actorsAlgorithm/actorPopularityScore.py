#AUTHOR : Diane Lantran
import pandas as pd
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys

current_directory = os.getcwd()

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
                            .until(EC.presence_of_element_located((by, name)))
    except TimeoutException:
        return None


### DATASETS ###
# movie dataset
file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'tmdb_5000_movies.csv')
movie_data = pd.read_csv(file_path)
# credit dataset
file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'tmdb_5000_credits.csv')
credits_data = pd.read_csv(file_path)
# actor dataset
file_path = os.path.join(current_directory, 'src', 'webscrapping_actor', 'actor.csv')
imdb_popularity_data = pd.read_csv(file_path, header=None, names=['Year', 'Title', 'Actor'])


# Function to filter movies by genre
def get_movies_by_genre(genre):
    # Convert the 'genres' column to a list of dictionaries
    movie_data['genres'] = movie_data['genres'].apply(eval)

    # Filter movies based on the specified genre
    filtered_movies = movie_data[movie_data['genres'].apply(lambda x: any(genre.lower() in d['name'].lower() for d in x))]

    # Return the titles of the filtered movies
    return filtered_movies['title'].tolist()


def get_actors_genre(movie_list):
    # returns a list containing all the actor and their order of appearance of a movie_list
    actors_list = []
    for i in range(0, credits_data.shape[0]) :
        movie = credits_data.loc[i, 'title']
        if movie in movie_list :
            cast = json.loads(credits_data.loc[i, 'cast'])
            for cast_member in cast:
                print("new guy")
                pop = 0
                ## si le nom est dans actor.csv il est populaire d apres imdb
                if cast_member['name'] in imdb_popularity_data['Actor']:
                    pop = 1
                nb_follow = scrapActorFollowers(cast_member['name'])
                time.sleep(15)
                actor_info = {
                    'name': cast_member['name'],
                    'order': cast_member['order'],
                    'popularity':pop, 
                    'nb_followers': nb_follow,
                    }
                actors_list.append(actor_info)
    print(actors_list)
    return(actors_list)            





def scrapActorFollowers(username):
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1]) 
        driver.get('https://www.google.ca/?hl=fr')
        success = False
        attempts = 0
        followers_count = None
        while((attempts < 4) and (success == False) ):
            try:
                search_box = waitForOneElement(driver, By.NAME, 'q')
                if search_box:
                    print("search box found")
                    search_box.send_keys(f'{username} on Instagram')
                    time.sleep(2)  # Wait for search results to load
                    search_box.submit()
                    time.sleep(2)  # Wait for search results to load
                    first_result = waitForOneElement(driver, By.CSS_SELECTOR, 'a[jsname="UWckNb"][href*="instagram.com"]')
                    if first_result:
                        first_result.click()
                        time.sleep(2)  # Wait for the profile to load
                        
                        followers_element = waitForOneElement(driver,By.XPATH,'//span[@class="_ac2a" and @title][1]')
                        if followers_element:
                            followers_count = followers_element.get_attribute('title')
                            print("nb followers : ", followers_count)
                            success = True
                            break
            except StaleElementReferenceException:
                print("StaleElementReferenceException, ", username)
                time.sleep(2)
                attempts += 1
        return(followers_count)    

#Tests : 
action_movies = get_movies_by_genre('Action')
actors_action = get_actors_genre(action_movies)

driver.quit() # Close the browser