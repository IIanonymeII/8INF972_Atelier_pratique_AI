#AUTHOR : Diane Lantran
import pandas as pd
import os
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
import matplotlib.pyplot as plt
import actorPopularityScrap
from scipy.stats import linregress
import numpy as np
from sklearn.metrics import mean_squared_error
from scipy.optimize import curve_fit


### DATASETS ###
current_directory = os.getcwd()
file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'forbes_celebrity_100.csv')
forbes_data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',')
file = os.path.join(current_directory, 'src', 'actorsAlgorithm', 'personalities_data.csv')
personalities_data = pd.read_csv(file, encoding='ISO-8859-1', sep=',')
fileActor = os.path.join(current_directory, 'src', 'actorsAlgorithm', 'popularity_data.csv')
popularity_data = pd.read_csv(file, encoding='ISO-8859-1', sep=',')

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

def addSalary():
    for index, row in forbes_data.iterrows():
        name = row['Name']
        salary = row['Pay (USD millions)']
        matching_index = personalities_data.index[personalities_data['Name'] == name]
        if not matching_index.empty:
            index_to_update = matching_index[0]
            personalities_data.at[index_to_update, 'Income'] = salary
    personalities_data.to_csv('src/actorsAlgorithm/personalities_data.csv', index=False)

def linear_regression(x, slope, intercept):
    return slope * x + intercept

def logarithmic_regression(x, a, b):
    return a * np.log(x) + b

def square_root_regression(x, a, b):
    return a * np.sqrt(x) + b

def polynomial_regression(x, *params):
    return np.polyval(params, x)

def plotIncomeVsScore():
    income = personalities_data['Income']
    score = personalities_data['Score']
    income = pd.to_numeric(income, errors='coerce')
    score = pd.to_numeric(score, errors='coerce')

    # Remove NaN values
    nan_mask = np.isnan(score) | np.isnan(income) | np.isinf(score) | np.isinf(income)
    income = income[~nan_mask]
    score = score[~nan_mask]

    if len(income) == 0:
        print("No valid samples remaining after NaN and Inf checks.")
        return

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.scatter(score, income, color='blue', marker='o', alpha=0.7)
    plt.xlabel('Score')
    plt.ylabel('Income (M US$)')
    plt.title('Income vs. Score')
    plt.grid(True)
    plt.savefig('src/graphs/incomeVSScore.png')
    plt.show()

def meanIncomeByScore():
    # Extract 'Income' and 'Score' columns
    income = personalities_data['Income']
    score = personalities_data['Score']

    # Convert 'Income' to numeric values
    income = pd.to_numeric(income, errors='coerce')

    # Remove NaN values
    nan_mask = np.isnan(score) | np.isnan(income) | np.isinf(score) | np.isinf(income)
    income = income[~nan_mask]
    score = score[~nan_mask]

    if len(income) == 0:
        print("No valid samples remaining after NaN and Inf checks.")
        return

    # Create a DataFrame with 'Income' and 'Score'
    df = pd.DataFrame({'Income': income, 'Score': score})

    # Group by the integer part of 'Score' and calculate the mean for each group
    df['ScoreInt'] = df['Score'].astype(int)
    mean_income_by_score = df.groupby('ScoreInt')['Income'].mean().reset_index()

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.scatter(mean_income_by_score['ScoreInt'], mean_income_by_score['Income'], color='blue', marker='o', alpha=0.7)
    plt.xlabel('Score (Integer Part)')
    plt.ylabel('Mean Income (M US$)')
    plt.title('Mean Income by Integer Part of Score')
    plt.grid(True)
    plt.savefig('src/graphs/meanIncomeByScoreInt.png')
    plt.show()


def meanIncomeByScoreRegression():
    # Extract 'Income' and 'Score' columns
    income = personalities_data['Income']
    score = personalities_data['Score']

    # Convert 'Income' to numeric values
    income = pd.to_numeric(income, errors='coerce')

    # Remove NaN values
    nan_mask = np.isnan(score) | np.isnan(income) | np.isinf(score) | np.isinf(income)
    income = income[~nan_mask]
    score = score[~nan_mask]

    if len(income) == 0:
        print("No valid samples remaining after NaN and Inf checks.")
        return

    # Create a DataFrame with 'Income' and 'Score'
    df = pd.DataFrame({'Income': income, 'Score': score})

    # Group by the integer part of 'Score' and calculate the mean for each group
    df['ScoreInt'] = df['Score'].astype(int)
    mean_income_by_score = df.groupby('ScoreInt')['Income'].mean().reset_index()

    # Scatter plot of mean income by integer part of 'Score'
    plt.figure(figsize=(10, 6))
    plt.scatter(mean_income_by_score['ScoreInt'], mean_income_by_score['Income'], color='blue', marker='o', alpha=0.7, label='Mean Income')

    # Linear regression
    slope, intercept, _, _, _ = linregress(mean_income_by_score['ScoreInt'], mean_income_by_score['Income'])
    linear_regression_line = linear_regression(mean_income_by_score['ScoreInt'], slope, intercept)
    linear_error = mean_squared_error(mean_income_by_score['Income'], linear_regression_line)
    plt.plot(mean_income_by_score['ScoreInt'], linear_regression_line, label=f'Linear Regression (Error: {linear_error:.4f})', color='red')

    # Logarithmic regression
    popt_log, _ = curve_fit(logarithmic_regression, mean_income_by_score['ScoreInt'], mean_income_by_score['Income'])
    logarithmic_regression_line = logarithmic_regression(mean_income_by_score['ScoreInt'], *popt_log)
    log_error = mean_squared_error(mean_income_by_score['Income'], logarithmic_regression_line)
    plt.plot(mean_income_by_score['ScoreInt'], logarithmic_regression_line, label=f'Logarithmic Regression (Error: {log_error:.4f})', color='green')

    # Square root regression
    popt_sqrt, _ = curve_fit(square_root_regression, mean_income_by_score['ScoreInt'], mean_income_by_score['Income'])
    sqrt_regression_line = square_root_regression(mean_income_by_score['ScoreInt'], *popt_sqrt)
    sqrt_error = mean_squared_error(mean_income_by_score['Income'], sqrt_regression_line)
    plt.plot(mean_income_by_score['ScoreInt'], sqrt_regression_line, label=f'Square Root Regression (Error: {sqrt_error:.4f})', color='purple')

    # Polynomial regression (adjust degree as needed)
    params_poly = np.polyfit(mean_income_by_score['ScoreInt'], mean_income_by_score['Income'], 2)  # Change the degree as needed
    poly_regression_line = polynomial_regression(mean_income_by_score['ScoreInt'], *params_poly)
    poly_error = mean_squared_error(mean_income_by_score['Income'], poly_regression_line)
    plt.plot(mean_income_by_score['ScoreInt'], poly_regression_line, label=f'Polynomial Regression (Error: {poly_error:.4f})', color='orange')

    estimateIncomeActors(params_poly)

    plt.xlabel('Score (Integer Part)')
    plt.ylabel('Mean Income')
    plt.title('Mean Income by Integer Part of Score with Regressions and Errors')
    plt.grid(True)
    plt.legend()
    plt.savefig('src/graphs/meanIncomeByScoreIntWithRegressionsAndErrors.png')
    plt.show()

def estimateIncomeActors(params_poly):
    popularity_data['Estimated_Income'] = polynomial_regression(popularity_data['Score'], *params_poly)
    popularity_data.to_csv('src/actorsAlgorithm/popularity_data.csv', index=False)


##########
###TEST###
##########


#keep_first_occurrence(forbes_data, file_path)
#keep_first_occurrence(personalities_data, file)
#scrapPersonality()
#addSalary()
#plotIncomeVsScore()
#meanIncomeByScore()
meanIncomeByScoreRegression()

