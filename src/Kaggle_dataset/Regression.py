import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import nltk
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from math import sqrt
from sklearn.compose import ColumnTransformer
import numpy as np
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, train_test_split
from sklearn.metrics import make_scorer, mean_squared_error
#RUN CODE BELOW IF FIRST TIME EXECUTING THIS SCRIPT
nltk.download('stopwords')

#Get dataset
data =pd.read_csv('tmdb_5000_movies.csv')


###################
# FEATURE SELECTION
###################

features = [
    'genres', 'runtime', 'keywords', 'budget', 'release_date', 'revenue','vote_average','vote_count','production_companies'
]

X = data[features]
colsToOneEncode = ["genres", 'keywords', "production_companies"]
for col in colsToOneEncode:
    unique_word = set()
    for col_list in X[col]:
        content = eval(col_list)  # Convert the string to a list of dictionaries
        for word in content:
            unique_word.add(word['name'])
    
    for word in unique_word:
        nb_col = X.shape[1]
        X.insert(nb_col, word, 0)
        
    for index, row in X.iterrows():
        content = eval(row[col])
        for word in content:
            X.at[index, word['name']] = 1
    X = X.drop(columns=[col])

###############################################
# REMOVING MISSING VALUES AND TOO SMALL VALUES
###############################################
X = X.dropna()

zeros_budget = X['budget'].eq(0).sum()
zeros_revenue = X['revenue'].eq(0).sum()

X = X.loc[X['revenue'] > 1000]
X = X.loc[X['budget'] > 1000]

####################################################################
#ENCODING CATEGORICAL DATA AND TRANSFORMING DATES TO NUMERICAL VALUE
####################################################################

# Feature Engineering
# Convert release_date to the year, month, and day
X['release_year'] = pd.to_datetime(data['release_date']).dt.year
X['release_month'] = pd.to_datetime(data['release_date']).dt.month
X['release_day'] = pd.to_datetime(data['release_date']).dt.day

X.drop('release_date', axis = 1, inplace=True)

##########################################
################FEATURE SCALING###########
##########################################

# Create a StandardScaler instance
X.columns = X.columns.astype(str)
columns_to_scale = ["budget", "release_year", "runtime", "vote_count"]
preprocessor = ColumnTransformer(
    transformers=[
        ('std_scaler', StandardScaler(), columns_to_scale),
    ],
    remainder='passthrough')

x_col_names = np.array(X.columns)
new_col_names = np.concatenate((columns_to_scale, np.delete(x_col_names, [0, 1, 4, -3])), axis=0)

X_transformed = preprocessor.fit_transform(X)
X = pd.DataFrame(X_transformed, columns=new_col_names)

###########################################
###############TRAINING MODEL##############
###########################################
X = X.dropna()
target = 'revenue'

from sklearn.decomposition import PCA
from sklearn.linear_model import Lasso, Ridge, ElasticNet

for i in range(1,13):
    current_X = X[X["release_month"] == i]
    y = current_X[target]
    current_X = current_X.drop(['revenue', "release_month"], axis = 1)
    current_X.columns = current_X.columns.astype(str)
    
    pca = PCA(n_components=0.9)
    X_pca = pca.fit_transform(current_X)
    
    
    
    X_train, X_test, y_train, y_test = train_test_split(X_pca, y, test_size=0.2, random_state=42)
    """
    n_estimators = [x * 10 for x in list(range(1,30))]
    param_grid = {
        'n_estimators': n_estimators
    }
    """
    
    print(f"\nnumber of lines for month n°{i}: {current_X.shape[0]}")
    
    lasso = Lasso()
    param_grid = {'alpha': [0.01, 0.1, 1.0, 10.0]}
    grid_search = GridSearchCV(lasso, param_grid, cv=5)
    grid_search.fit(X_train, y_train)
    best_lasso_model = grid_search.best_estimator_
    lasso_predictions = best_lasso_model.predict(X_test)
    lasso_rmse = mean_squared_error(y_test, lasso_predictions, squared=False)
    print(f"Lasso RMSE on test set: {lasso_rmse}")
    
    ridge = Ridge()
    param_grid = {'alpha': [0.01, 0.1, 1.0, 10.0]}
    ridge_grid_search = GridSearchCV(ridge, param_grid, cv=5)
    ridge_grid_search.fit(X_train, y_train)
    best_ridge_model = ridge_grid_search.best_estimator_
    ridge_predictions = best_ridge_model.predict(X_test)
    ridge_rmse = mean_squared_error(y_test, ridge_predictions, squared=False)
    print(f"Ridge RMSE on test set: {ridge_rmse}")
    
    elastic_net = ElasticNet()
    param_grid = {
        'alpha': [0.01, 0.1, 1.0, 10.0],
        'l1_ratio': [0.1, 0.5, 0.7, 0.9]
    }
    elastic_net_grid_search = GridSearchCV(elastic_net, param_grid, cv=5)
    elastic_net_grid_search.fit(X_train, y_train)
    best_elastic_net_model = elastic_net_grid_search.best_estimator_
    elastic_net_predictions = best_elastic_net_model.predict(X_test)
    elastic_net_rmse = mean_squared_error(y_test, elastic_net_predictions, squared=False)
    print(f"Elastic Net RMSE on test set: {elastic_net_rmse}")
    
    rf_regressor = RandomForestRegressor()
    n_estimators = [x * 10 for x in list(range(1,30))]
    param_grid = {
        'n_estimators': n_estimators
    }
    grid_search = GridSearchCV(rf_regressor, param_grid, cv=5, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)
    best_params = grid_search.best_params_
    rmse_scorer = make_scorer(lambda y, y_pred: np.sqrt(mean_squared_error(y, y_pred)), greater_is_better=False)
    best_rf_regressor = RandomForestRegressor(**best_params)
    best_rf_regressor.fit(X_train, y_train)
    y_pred = best_rf_regressor.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"Tree on test set: {rmse}")
    