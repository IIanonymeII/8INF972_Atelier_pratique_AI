# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 15:28:00 2023

@author: basil
"""
# General imports
import pandas as pd

# Preprocessing imports
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import nltk
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
# Classification imports
import joblib
# Classification results imports
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
import json
# Get dataset
df = pd.read_csv("data/oscars_with_genres.csv")

threshold_year = 2022

target_cols = ['Main_nominations', 'Technical_nominations', 
               'Artistic_nominations', 'Main_winner', 'Technical_winner', 
               'Artistic_winner']
cluster_cols = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 
               'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 
               'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction', 
               'TV Movie', 'Thriller', 'War', 'Western']


nltk.download('stopwords')

def createNewTargetCols(df):
    df["TTL_noms"] = df["Main_nominations"] + df ["Technical_nominations"] + df["Artistic_nominations"]
    df["is_nom"] = df["TTL_noms"] > 0
    df["TTL_wins"] = df["Main_winner"] + df ["Technical_winner"] + df["Artistic_winner"]
    df["is_win"] = df["TTL_wins"] > 0
    


def removeData(df, percentage = 0.5):
    df_no_oscars = df[(df[target_cols] == 0).all(axis=1)]
    
    df_no_oscars.loc[:, 'count'] = df_no_oscars.groupby('Year').cumcount() + 1
    
    df_no_oscars_filtered = df_no_oscars[df_no_oscars['count'] <= df_no_oscars.groupby('Year')['count'].transform('max') * percentage]
    df_no_oscars_filtered = df_no_oscars_filtered.drop('count', axis=1)
    df = pd.concat([df[(df[target_cols] > 0).any(axis=1)], 
                    df_no_oscars_filtered], ignore_index=True)


# Change dataset (remove rows, add cols)
createNewTargetCols(df)
removeData(df, 0.2)

# One hot encode the keywords
stop_words = set(stopwords.words('english'))
df['Keywords'] = df['Keywords'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))
tfidf_vectorizer = TfidfVectorizer(min_df=40)  # Adjust min_df as needed
keyword_tfidf = tfidf_vectorizer.fit_transform(df['Keywords'])
keywords = tfidf_vectorizer.get_feature_names_out()
df = pd.concat([df, pd.DataFrame(keyword_tfidf.toarray(), columns=keywords)], axis=1)
df.drop('Keywords', axis = 1, inplace=True)
df.columns = df.columns.astype(str)


# Prepare preprocess
cluster_cols = cluster_cols + list(keywords)
with open("data/columns_oscars.json", 'w') as json_file:
    json.dump(cluster_cols, json_file)
X = df[cluster_cols]
y = df["is_nom"]

# Standardize
scaler = StandardScaler()
X.loc[:, cluster_cols] = scaler.fit_transform(X[cluster_cols])

standardization_params = {
    'mean': scaler.mean_.tolist(),
    'std': scaler.scale_.tolist()
}

with open("data/standardization_params.json", 'w') as json_file:
    json.dump(standardization_params, json_file)

# 
pca = PCA(n_components=0.9)
pca.fit(X)
X = pca.transform(X)
joblib.dump(pca, 'models/pca_oscars.joblib')


# train_test separation
X_train = X[df["Year"] < threshold_year]
X_test = X[df["Year"] >= threshold_year]
y_train = y[df["Year"] < threshold_year]
y_test = y[df["Year"] >= threshold_year]

clf = LogisticRegression(C = 0.1)
clf.fit(X_train, y_train)
filename = 'models/oscar_prediction.joblib'
joblib.dump(clf, filename)
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, digits = 4))
