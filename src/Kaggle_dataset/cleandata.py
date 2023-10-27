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

#RUN CODE BELOW IF FIRST TIME EXECUTING THIS SCRIPT
nltk.download('stopwords')

#Get dataset
data =pd.read_csv('src/Kaggle_dataset/tmdb_5000_movies.csv')


###################
# FEATURE SELECTION
###################

features = [
    'title','genres', 'keywords', 'runtime', 'budget', 'release_date', 'revenue','vote_average','vote_count','production_companies'
]

X = data[features]

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

#Using TFDIF to encode: (keywords, genres, titles and production companies), first we remove stopwords

stop_words = set(stopwords.words('english'))

X['keywords'] = X['keywords'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))
X['genres'] = X['genres'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))
X['title'] = X['title'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))
X['production_companies'] = X['production_companies'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))

#We create the vectorizer that will be used to encode the string values
tfidf_vectorizer = TfidfVectorizer(min_df=40)  # Adjust min_df as needed
tfidf_vectorizer_2 = TfidfVectorizer(min_df=40)  # Adjust min_df as needed
tfidf_vectorizer_3 = TfidfVectorizer(min_df=40)  # Adjust min_df as needed
tfidf_vectorizer_4 = TfidfVectorizer(min_df=40)  # Adjust min_df as needed

#We fit the vectorizer to the column of string values
keyword_tfidf = tfidf_vectorizer.fit_transform(X['keywords'])
keyword_tfidf_2 = tfidf_vectorizer_2.fit_transform(X['genres'])
keyword_tfidf_3 = tfidf_vectorizer_3.fit_transform(X['title'])
keyword_tfidf_4 = tfidf_vectorizer_4.fit_transform(X['production_companies'])

#We add the encoded values to the dataframe
X = pd.concat([X, pd.DataFrame(keyword_tfidf.toarray())], axis=1)
X = pd.concat([X, pd.DataFrame(keyword_tfidf_2.toarray())], axis=1)
X = pd.concat([X, pd.DataFrame(keyword_tfidf_3.toarray())], axis=1)
X = pd.concat([X, pd.DataFrame(keyword_tfidf_4.toarray())], axis=1)

#We drop the old columns that contain the string values
X.drop('keywords', axis = 1, inplace=True)
X.drop('genres', axis = 1, inplace=True)
X.drop('release_date', axis = 1, inplace=True)
X.drop('title', axis = 1, inplace=True)
X.drop('production_companies', axis = 1, inplace=True)

# Feature Engineering
# Convert release_date to the year, month, and day
X['release_year'] = pd.to_datetime(data['release_date']).dt.year
X['release_month'] = pd.to_datetime(data['release_date']).dt.month
X['release_day'] = pd.to_datetime(data['release_date']).dt.day

##########################################
################FEATURE SCALING###########
##########################################

max_before = X['budget'].max()
min_before = X['budget'].min()
range_before = max_before - min_before

# Create a StandardScaler instance
scaler_budget = StandardScaler()
scaler_year = StandardScaler()
scaler_runtime = StandardScaler()
scaler_votecount = StandardScaler()

# Fit the scaler to the data and transform the columns
column_name = 'budget'
column_2 = 'release_year'
column_3 = 'runtime'
column_4 = 'vote_count'

X[column_name] = scaler_budget.fit_transform(X[[column_name]])
X[column_2] = scaler_year.fit_transform(X[[column_2]])
X[column_3] = scaler_runtime.fit_transform(X[[column_3]])
X[column_4] = scaler_votecount.fit_transform(X[[column_4]])

###########################################
###############TRAINING MODEL##############
###########################################

# Select relevant columns
X = X.dropna()
target = 'revenue'
y = X[target]
X.drop('revenue', axis = 1, inplace=True)
X.columns = X.columns.astype(str)

print(X.head(5))
print("X shape " + str(X.shape))
print(y.head(5))
print("Y shape " + str(y.shape))

# Create lists to store RMSE values and complexities
rmse_values = []
complexities = []
best_rmse = 130000000
best_complexity = 0
counter = 0

# Define a range of complexities (e.g., number of trees in the Random Forest)
for complexity in range(1,30):
    print(f"Training model with complexity {complexity}...")

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train a Random Forest Regressor model with the current complexity
    model = RandomForestRegressor(n_estimators=complexity * 10, random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions on the testing data
    y_pred = model.predict(X_test)
    
    # Calculate RMSE
    rmse = sqrt(mean_squared_error(y_test, y_pred))

    if rmse < best_rmse:
        best_rmse = rmse
        best_complexity = complexity*10
    
    # Save RMSE and complexity
    rmse_values.append(rmse)
    complexities.append(complexity * 10)  # You can adjust this if the complexity measure is different
    
    print(f"RMSE for complexity {complexity}: {rmse}")

formatted_rmse = "{:.2e}".format(best_rmse)  # {:.2e} specifies 2 decimal places in scientific notation
print("Best rmse formatted" + str(formatted_rmse))
print("Best rmse " + str(best_rmse))
print("Best complexity " + str(best_complexity))

# Plot RMSE values against complexity
plt.figure(figsize=(10, 6))
plt.plot(complexities, rmse_values, marker='o')
plt.title('RMSE vs. Model Complexity')
plt.xlabel('Model Complexity (Number of Trees)')
plt.ylabel('RMSE')
plt.grid(True)
plt.show()



