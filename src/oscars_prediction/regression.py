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
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree

# Classification results imports
from sklearn.metrics import classification_report

# Get dataset
df = pd.read_csv(r'../../data/oscars_with_genres.csv')

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
df = pd.concat([df, pd.DataFrame(keyword_tfidf.toarray())], axis=1)
df.drop('Keywords', axis = 1, inplace=True)
df.columns = df.columns.astype(str)

# Prepare preprocess
cluster_cols = cluster_cols + list(map(str,range(0,keyword_tfidf.shape[1])))
X = df[cluster_cols]
y = df["is_nom"]

# Standardize
X.loc[:, cluster_cols] = StandardScaler().fit_transform(X[cluster_cols])

# 
pca = PCA(n_components=0.9)
X = pca.fit_transform(X)


# train_test separation
X_train = X[df["Year"] < threshold_year]
X_test = X[df["Year"] >= threshold_year]
y_train = y[df["Year"] < threshold_year]
y_test = y[df["Year"] >= threshold_year]

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.decomposition import PCA
"""
# Create a list of classifiers
classifiers = [
    ('KNN', KNeighborsClassifier()),
    ('Decision Tree', DecisionTreeClassifier()),
    ('Random Forest', RandomForestClassifier()),
    ('SVM', SVC()),
    ('Logistic Regression', LogisticRegression()),
    ('Naive Bayes', MultinomialNB()),
    ('Neural Network', MLPClassifier())  # Add MLPClassifier
]


# Define hyperparameter grids for grid search for each classifier



param_grids = {
    'KNN': {
        'classifier__n_neighbors': [2, 3, 4, 5, 7, 9, 15],
        'classifier__p': [1, 2]
    },

    'Decision Tree': {
        'classifier__max_depth': [None, 5, 10],
        'classifier__min_samples_split': [2, 5]
    },
    'Random Forest': {
        'classifier__n_estimators': [10, 50, 100, 250],
        'classifier__max_depth': [None, 5, 10]
    },
    'SVM': {
        'classifier__C': [0.1, 0.5, 1.0, 10.0, 15.0],
        'classifier__kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
        'classifier__degree': [2, 3, 5, 7],
    },
    'Logistic Regression': {
        'classifier__C': [0.1, 0.5, 1.0, 10.0],
    },
    'Neural Network': {
        'classifier__hidden_layer_sizes': [(50, 50), (100, 50, 25)],
        'classifier__activation': ['relu', 'tanh'],
        'classifier__max_iter': [1000],
    }
}

# Create a custom pipeline for each classifier and perform grid search over 10 folds
for name, classifier in classifiers:
    if name in ('SVM', 'Naive Bayes', 'Logistic Regression'):
        clf_pipeline = Pipeline(steps=[
            ('classifier', classifier)
        ])
    else:
        clf_pipeline = Pipeline(steps=[
            ('pca', PCA(n_components=0.90)),
            ('classifier', classifier)
        ])

    # Perform grid search with 10-fold cross-validation
    grid_search = GridSearchCV(clf_pipeline, param_grids[name], 
                               scoring='accuracy', cv=10, verbose=4)
    scores = grid_search.fit(X, y)
    best_params = grid_search.best_params_
    best_accuracy = grid_search.best_score_
    print(f'Best Estimator for {name}:\n{best_params}')
    print(f'Best Accuracy for {name}: {best_accuracy:.2f}\n')
"""
    


# Classification
clf = RandomForestClassifier(n_estimators = 250, max_depth = 10)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, digits = 4))

clf = LogisticRegression(C = 0.1)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, digits = 4))

y = df["is_win"]

y_train = y[df["Year"] < threshold_year]
y_test = y[df["Year"] >= threshold_year]

clf = RandomForestClassifier(n_estimators = 250, max_depth = 10)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, digits = 4))

clf = LogisticRegression(C = 0.1)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, digits = 4))