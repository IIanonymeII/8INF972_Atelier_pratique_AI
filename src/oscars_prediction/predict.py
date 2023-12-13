import joblib
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np
import json
from sklearn.preprocessing import StandardScaler

def predict(genres, keywords):
    model = joblib.load("models/oscar_prediction.joblib")
    pca = joblib.load("models/pca_oscars.joblib")
    with open("data/columns_oscars.json", 'r') as json_file:
        col_names = json.load(json_file)
    with open("data/standardization_params.json", 'r') as json_file:
        standardization_params = json.load(json_file)
    
    all_genres = col_names[0:19]
    all_keywords = col_names[19:]
    dummy_df = pd.DataFrame(columns=all_genres)
    
    new_genres = np.zeros(len(all_genres))
    new_genres[dummy_df.columns.isin(genres)] = 1
    genreDF = pd.DataFrame([new_genres], columns=all_genres)
    
    dummy_df = pd.DataFrame(columns=all_keywords)
    new_keywords = np.zeros(len(all_keywords))
    new_keywords[dummy_df.columns.isin(keywords)] = 1
    keywordDF = pd.DataFrame([new_keywords], columns=all_keywords)
    
    X = pd.concat([genreDF, keywordDF], axis=1)
    X = (X - np.array(standardization_params['mean'])) / np.array(standardization_params['std'])
    X = pca.transform(X)
    prediction = model.predict(X.reshape(1, -1))
    return prediction[0]
    