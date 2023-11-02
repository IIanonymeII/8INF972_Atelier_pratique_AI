import pandas as pd
from sklearn.impute import KNNImputer

# Step 1: Concatenate all CSV files into one DataFrame
dfs = [pd.read_csv("src/the_numbers/movies" + str(year) + ".csv") for year in range(1930, 2016)]
df = pd.concat(dfs, ignore_index=True)

# Step 2: Handle missing values
# For 'MPAA Rating', replace missing values with the most common one amongst the 1 nearest neighbors
# knn_imputer = KNNImputer(n_neighbors=1)
# df['MPAA Rating'] = knn_imputer.fit_transform(df[['MPAA Rating']])

# For the following columns, set missing values to 0
columns_to_fill_with_zero = ['Original domestic B.O', 'Original international B.O',
                             'Adjusted domestic B.O', 'Adjusted international B.O']
df[columns_to_fill_with_zero] = df[columns_to_fill_with_zero].fillna(0)

# Step 3: Create new columns
df['Total original B.O'] = df['Original domestic B.O'] + df['Original international B.O']
df['Total adjusted B.O'] = df['Adjusted domestic B.O'] + df['Adjusted international B.O']

# Step 4: Handle missing values for 'Original budget' and 'Duration'
columns_to_impute = ['Original budget', 'Duration']
knn_imputer = KNNImputer(n_neighbors=15)
df[columns_to_impute] = knn_imputer.fit_transform(df[columns_to_impute])
df.to_csv('src/the_numbers/movies1930_2014.csv', index=False)
# Now, you have a preprocessed DataFrame with all the required transformations.