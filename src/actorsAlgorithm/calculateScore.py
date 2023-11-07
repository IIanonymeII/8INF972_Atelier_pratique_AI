#AUTHOR : Diane Lantran
import os
import pandas as pd
import numpy as np
import pandas as pd
from io import StringIO
from datetime import datetime
import actorDataNormalisation
import matplotlib.pyplot as plt

### INSTAGRAM WEBSCRAPPING DATAS ###
current_directory = os.getcwd()
file_path = os.path.join(current_directory, 'src', 'actorsAlgorithm', 'popularity_data.csv')
instascrap_file = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',')

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
    
def interpretTrend(trend_data, followers):
    dates = trend_data['Semaine']
    values = trend_data['Value']

    # Convert 'Semaine' to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(dates):
        dates = pd.to_datetime(dates)

    # Check if the data has at least two points for linear regression
    if len(dates) < 2:
        print("Insufficient data for linear regression.")
        return None

    days_since_start = (dates - dates.min()).dt.days.values
    coefficients = np.polyfit(days_since_start, values, 1)
    leading_coefficient = coefficients[0]
    score = followers*(1+leading_coefficient)
    return score

def getNbFollowers(actor_name):
    actor_row = instascrap_file[instascrap_file['Actor'] == actor_name]
    if not actor_row.empty:
        nb_followers = actor_row['Followers'].values[0]
        print(actor_name, " has ", nb_followers, " followers")
        nb_followers = pd.to_numeric(nb_followers, errors='coerce')
        return(nb_followers)
    else:
        print("Can't access ", actor_name, "number of followers !")
        return(None)

def calculateActorScore(actor_name):
    followers = getNbFollowers(actor_name)
    trend_data = getGoogleTrendData(actor_name)
    if trend_data is not None :
        score = interpretTrend(trend_data, followers)
        print(actor_name, ', score : ', score)
        return(score)
    

def addScoreToDataSet():
    actorDataNormalisation.cleanActorDataSet()
    scores = []
    for index, row in instascrap_file.iterrows():
        actor_name = row['Actor']
        scores.append(calculateActorScore(actor_name))
    instascrap_file['Score'] = scores
    instascrap_file.to_csv('src/popularity_scores.csv', index=False)

def getStandardizedScore():
    addScoreToDataSet()
    scores = instascrap_file['Score']
    instascrap_file['Score'] = normCentreRed(scores) #ou normCentreRed(scores)

def norm_standard(scores):
    # pas concluant après visualisation
    min_score = min(scores)
    max_score = max(scores)
    scores_filled = scores.fillna(0)
    normalized_scores = [int(((score - min_score) / (max_score - min_score)) * 100) for score in scores_filled]

    instascrap_file['Score']=normalized_scores
    instascrap_file.to_csv('src/popularity_scores.csv', index=False)
    showScoresRepartition("actorScoresStandardises")
    return(normalized_scores)

def normCentreRed(scores):
    # Remplacer les valeurs manquantes par la moyenne
    mean_score = np.nanmean(scores)
    scores_filled = scores.fillna(mean_score)

    # Calcul de l'écart type
    std_dev = np.nanstd(scores_filled)

    # Normalisation centrée réduite
    normalized_scores = [(score - mean_score) / std_dev for score in scores_filled]

    # Rééchelonnage entre 0 et 100
    min_normalized = min(normalized_scores)
    max_normalized = max(normalized_scores)
    scaled_scores = [int((score - min_normalized) / (max_normalized - min_normalized) * 100) for score in normalized_scores]

    instascrap_file['Score']=scaled_scores
    instascrap_file.to_csv('src/popularity_scores.csv', index=False)
    showScoresRepartition("actorScoresNCR")

    return normalized_scores

def showScoresRepartition(filename):
    scores = instascrap_file['Score']
    score_counts = {}
    for score in scores:
        score_counts[score] = score_counts.get(score, 0) + 1

    # Create lists for plotting
    unique_scores = list(score_counts.keys())
    actor_counts = [score_counts[score] for score in unique_scores]

    save_path = "src/graphs/" + filename

    # Plotting the graph
    plt.bar(unique_scores, actor_counts, color='blue')
    plt.xlabel('Scores')
    plt.ylabel("Nombre d'acteurs")
    plt.title("Etalement d'histogramme des scores")
    plt.savefig(save_path)
    plt.show()

getStandardizedScore()
