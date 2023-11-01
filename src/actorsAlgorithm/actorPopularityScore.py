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
import shutil
import webbrowser


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

def get_download_folder():
    # Get the user's home directory
    home_directory = os.path.expanduser("~")

    # Combine the home directory with the default Downloads folder name
    download_folder = os.path.join(home_directory, "Downloads")

    return download_folder

###SETS CONSTANTS ###
current_directory = os.getcwd()
default_download = get_download_folder()

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
        i = 0
        if movie in movie_list :
            cast = json.loads(credits_data.loc[i, 'cast'])
            j = 0
            for cast_member in cast:
                print("film : ", i, "/", credits_data.shape[0], ", actor : ", j, "/", len(cast))
                pop = 0
                ## si le nom est dans actor.csv il est populaire d apres imdb
                if cast_member['name'] in imdb_popularity_data['Actor']:
                    pop = 1
                
                scrapActorGoogleTrends(cast_member['name'])
                nb_follow = scrapActorFollowers(cast_member['name'])
                
                #time.sleep(15)
                actor_info = {
                    'name': cast_member['name'],
                    'order': cast_member['order'],
                    'popularity':pop, 
                    'nb_followers': nb_follow,
                    }
                actors_list.append(actor_info)
                j+=1
            i+=1
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

def scrapActorGoogleTrends(username):
        
        success = False
        attempts = 0
        while((attempts < 4) and (success == False) ):
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1]) 
            driver.get('https://trends.google.fr/trends?geo=US&hl=fr')
            try:
                search_box = waitForOneElement(driver, By.ID, 'i7') #access the google trends search box
                if search_box:
                    search_box.clear()
                    search_box.send_keys(f'{username}')
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(2)  # Wait for search results to load
                    
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
                    time.sleep(2)
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
action_movies = get_movies_by_genre('Action')
actors_action = get_actors_genre(action_movies)

driver.quit() # Close the browser