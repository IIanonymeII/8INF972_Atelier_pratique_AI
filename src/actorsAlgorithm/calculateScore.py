#AUTHOR : Diane Lantran
import os
import pandas as pd
import numpy as np
import pandas as pd
from io import StringIO
from datetime import datetime
import actorDataNormalisation
import matplotlib.pyplot as plt
import os
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
import math
import shutil

def get_download_folder():
    home_directory = os.path.expanduser("~")
    download_folder = os.path.join(home_directory, "Downloads")
    return download_folder

ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
default_download = get_download_folder()
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
    # Get the user's home directory
    home_directory = os.path.expanduser("~")

    # Combine the home directory with the default Downloads folder name
    download_folder = os.path.join(home_directory, "Downloads")

    return download_folder


### INSTAGRAM WEBSCRAPPING DATAS ###
current_directory = os.getcwd()
file_path = os.path.join(current_directory, 'src', 'actorsAlgorithm', 'popularity_data.csv')
instascrap_file = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',')
file_path_l = os.path.join(current_directory, 'src', 'actorsAlgorithm', 'personalities_data.csv')
learning_file = pd.read_csv(file_path_l, encoding='ISO-8859-1', sep=',')


### GET FUNCTIONS ###
def getGoogleTrendData(actor_name):
    file_name = actor_name+'_trend.csv'
    file_path = os.path.join(current_directory, 'src', 'actor_trends_treated', file_name)
    try :
        actor_trend_file = pd.read_csv(file_path, sep=',')
        return(actor_trend_file)
    except FileNotFoundError:
        print(actor_name, " trend file not found !")
        actorDataNormalisation.deleteActorPopularityRecord(actor_name)
        return(None)

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
                        
                        time.sleep(2)  # Wait for the file to download
                        src_path = os.path.join(default_download,'multiTimeline.csv')
                        dest_path = os.path.join("src","actor_trends_scrap", f"{username}_trend.csv")
                        if os.path.exists(src_path):
                            if os.path.exists(dest_path):
                                os.replace(src_path, dest_path)
                                print("replaced")
                            else:
                                shutil.move(src_path, dest_path)
                                print('pas trouvé ?')

                            # Set success to True since the operation completed
                            success = True
                    attempts +=1

            except StaleElementReferenceException:
                print("StaleElementReferenceException, ", username)
                time.sleep(2)
                attempts += 1  
    
def interpretTrend(actor_name, trend_data, followers):
    if 'Semaine' in trend_data:
        dates = trend_data['Semaine']
        values = trend_data['Value']

        # Convert 'Semaine' to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(dates):
            dates = pd.to_datetime(dates)

        # Check if the data has at least two points for linear regression
        if len(dates) < 2:
            print("Insufficient data for linear regression.")
            scrapActorGoogleTrends(actor_name)

        days_since_start = (dates - dates.min()).dt.days.values
        coefficients = np.polyfit(days_since_start, values, 1)
        leading_coefficient = coefficients[0]
        if followers != 0 :
            score = math.log(followers)*(1+leading_coefficient)
        else : 
            score = 0
        return score
    else:
        scrapActorGoogleTrends(actor_name)


def getNbFollowers(actor_name):
    actor_row = instascrap_file[instascrap_file['Actor'] == actor_name]
    actor_row = learning_file[learning_file['Name'] == actor_name]
    if not actor_row.empty:
        nb_followers = actor_row['Followers'].values[0]
        nb_followers = pd.to_numeric(nb_followers, errors='coerce')
        return(nb_followers)
    else:
        print("Can't access ", actor_name, "number of followers !")
        return(None)

def calculateActorScore(actor_name):
    followers = getNbFollowers(actor_name)
    trend_data = getGoogleTrendData(actor_name)
    if trend_data is not None :
        score = interpretTrend(actor_name, trend_data, followers)
        print(actor_name, ', score : ', score)
        return(score)
    

def addScoreToDataSet():
    actorDataNormalisation.cleanActorDataSet()
    scores = []
    for index, row in learning_file.iterrows():
    #for index, row in instascrap_file.iterrows():
        #actor_name = row['Actor']
        actor_name = row['Name']
        scores.append(calculateActorScore(actor_name))
    #instascrap_file['Score'] = scores
    #instascrap_file.to_csv('src/actorsAlgorithm/popularity_data.csv', index=False)
    learning_file['Score'] = scores
    learning_file.to_csv('src/actorsAlgorithm/personalities_data.csv', index=False)

def getStandardizedScore():
    addScoreToDataSet()
    #scores = instascrap_file['Score']
    scores = learning_file['Score']
    #instascrap_file['Score'] = normCentreRed(scores)#normCentreRed(scores) #ou norm_standard(scores)
    

def showScoresRepartition():
    scoresTest = instascrap_file['Score']
    scoresLearning = learning_file['Score']
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.hist([scoresTest, scoresLearning], bins=20, alpha=0.7, label=['Scores Test', 'Scores Learning'])

    plt.xlabel('Score Range')
    plt.ylabel('Number of Persons')
    plt.title('Score Repartition Comparison')
    plt.savefig('src/graphs/scoresRepartition.png')
    plt.legend()
    plt.grid(True)
    plt.show()

#getStandardizedScore()
showScoresRepartition()