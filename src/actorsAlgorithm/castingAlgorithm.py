#AUTHOR : Diane Lantran
import pandas as pd
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys

################
### DATASETS ###
################
# current_directory = os.getcwd()  # le probleme c'est que il retourn le repertoire de travail courant, c'est  dire à partir d'ou le fichier principal est lancé, ex: si je le lance a la racine et que j'appel ce fichier il va retourné C: et pas ou le fichier castingAlgorithm.py est

# Obtenez le chemin absolu du fichier
file_path = os.path.abspath(__file__)
# Obtenez le répertoire du fichier
file_directory = os.path.dirname(file_path)
current_directory = os.path.dirname(os.path.dirname(file_directory))

# movie dataset
file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'tmdb_5000_movies.csv')
movie_data = pd.read_csv(file_path)
# credit dataset
file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'tmdb_5000_credits.csv')
credits_data = pd.read_csv(file_path)
# actor score generated dataset
file_path = os.path.join(current_directory, 'src', 'actorsAlgorithm', 'popularity_data.csv')
popularity_data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',')
# oscar dataset
file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'oscardata_acting.csv')
oscar_data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',')


#######################
### SCRAPPING UTILS ###
#######################
def create_driver():
    firefox_options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(service=FirefoxService(executable_path=GeckoDriverManager().install()), options=firefox_options)
    return driver
# driver = create_driver()
def waitForOneElement(driver, by, value):
    ignored_exceptions = (NoSuchElementException,StaleElementReferenceException)  # Ignore NoSuchElementException
    try:
        return WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        return None

def get_download_folder():
    home_directory = os.path.expanduser("~")
    download_folder = os.path.join(home_directory, "Downloads")
    return download_folder

#################
### ALGORITHM ###
#################
def  findActorsBOXOFFICE(castSize, genres, budgetMin, budgetMax):
    # castSize : nombre d'acteurs à retourner
    # genres : liste des genres selectionnés par l'utilisateur
    # budgetMin / budgetMax : selection par le slider

    candidates = getActorGenre(genres)
    [minActorSalary, maxActorSalary] = getSalaryBudget(castSize, genres, budgetMin, budgetMax) #la proportion du budget allouée aux salaire varie en fonction du genre et du budget voulu
    candidates = filterCandidates(candidates, minActorSalary, maxActorSalary) #filtre par le salaire & classe par ordre de popularité
   
    #retourne les castSize premiers
    print(candidates)
    if candidates is not None :
        #random sur les castSize*2 premiers pour ne pas retourner toujours les mêmes
        if len(candidates)>2*castSize:
            candidates = candidates[:2*castSize]
            random.shuffle(candidates)
        random_candidates = candidates[:castSize]
        return random_candidates
    else :
        return None


def getActorGenre(genres):
    print("genres for candidates: ", genres)
    threshold = 0.7 #i want 70% of matching genres
    similarMovies = get_movies_by_genres(genres, threshold)
    similarMoviesActors = getActorsFromMovies(similarMovies)
    return(similarMoviesActors)

def get_movies_by_genres(genres, threshold):
    matching_movies = []
    for index, row in movie_data.iterrows():
        movie_genres = [genre['name'] for genre in eval(row['genres'])]
        matching_percentage = sum(genre in movie_genres for genre in genres) / len(genres)
        if matching_percentage >= threshold:
            matching_movies.append(row['original_title'])
    if (len(matching_movies) == 0 and threshold > 0) :
        threshold = threshold -0.1
        return get_movies_by_genres(genres, threshold)
    else :
        return matching_movies
    
def get_all_genres():
    all_genres = []
    for index, row in movie_data.iterrows():
        movie_genres = [genre['name'] for genre in eval(row['genres'])]
        all_genres.extend(movie_genres)
    return list(set(all_genres)) # unique list

def getActorsFromMovies(similarMovies):
    actors = []
    for movie in similarMovies:
        credits_row = credits_data[credits_data['title'] == movie]
        if not credits_row.empty:
            # Extract the cast information
            cast_info = eval(credits_row['cast'].iloc[0])
            actors.extend([actor['name'] for actor in cast_info])
    return(actors)

def getSalaryBudget(castSize, genres, budgetMin, budgetMax):
    coef = 1.7
    if ('Documentaire' and 'Animation' in genres):
        proportion = coef*(0.04+0.13)/2
    elif ('Animation' in genres):
        proportion = coef*0.13
    elif ('Documentaire' in genres):
        proportion = coef*0.04        
    else:
        proportion = coef*0.1
    min = budgetMin*proportion/castSize
    max = budgetMax*proportion/castSize
    salaryBudget = [min, max]    
    return(salaryBudget) 

def filterCandidates(candidates, minActorSalary, maxActorSalary):
    popularity_data_filtered = popularity_data[
        (popularity_data['Actor'].isin(candidates)) &
        (minActorSalary < popularity_data['EstimatedIncome'] * 1000000) &
        (popularity_data['EstimatedIncome'] * 1000000 < maxActorSalary)
    ]

    sortedCandidates = popularity_data_filtered.sort_values(by='Score', ascending=False)
    result = list(sortedCandidates['Actor'])
    return result

def findActorsOSCAR():
    #tard plus
    True


###TEST###
#findActorsBOXOFFICE(5, ['Action'], 1, 100000000) #rien pour moins d'un 0.5 Milliard de dollars...
#print('matching movies : ',get_movies_by_genres(['Thriller', 'Comedy', 'Adventure', 'Action', 'Drama', 'Romance', 'Family', 'Horror', 'Animation'], 1))
#print('cast : ', getActorsFromMovies(get_movies_by_genres(['Thriller', 'Comedy', 'Adventure', 'Action', 'Drama', 'Romance', 'Family', 'Horror', 'Animation'], 1)))