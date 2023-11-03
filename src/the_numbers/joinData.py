import pandas as pd
from sklearn.impute import KNNImputer, SimpleImputer
import ast

def parse_list_string(s):
    try:
        return ast.literal_eval(s)
    except (SyntaxError, ValueError):
        return []


# Step 1: Concatenate all CSV files into one DataFrame
dfs = [pd.read_csv("movies" + str(year) + ".csv") for year in range(1930, 2022)]
df = pd.concat(dfs, ignore_index=True)


# Step 2: Handle missing values
# For 'MPAA Rating', replace missing values with the most common one amongst the 1 nearest neighbors
df['MPAA Rating'] = df["MPAA Rating"].fillna("Not Rated")

# For the following columns, set missing values to 0
columns_to_fill_with_zero = ['Original domestic B.O', 'Original international B.O',
                             'Adjusted domestic B.O', 'Adjusted international B.O']
df[columns_to_fill_with_zero] = df[columns_to_fill_with_zero].fillna(0)

# Step 3: Create new columns
df['Total original B.O'] = df['Original domestic B.O'] + df['Original international B.O']
df['Total adjusted B.O'] = df['Adjusted domestic B.O'] + df['Adjusted international B.O']

df['Genres'] = df['Genres'].apply(parse_list_string)

df = df.dropna(subset=['Original budget'])

print("Missing values:")
missing_values_per_column = df.isna().sum()
print(missing_values_per_column)


columns_to_impute = ["Year", "Month"]
knn_imputer = KNNImputer(n_neighbors=5, weights='distance')
df[columns_to_impute] = knn_imputer.fit_transform(df[columns_to_impute])


columns_to_impute = ["Original budget", "Adjusted budget"]
median_imputer = SimpleImputer(strategy='median')
df[columns_to_impute] = median_imputer.fit_transform(df[columns_to_impute])

# Step 4: Handle missing values for 'Original budget' and 'Duration'
columns_to_impute = ['Duration']
knn_imputer = KNNImputer(n_neighbors=15)
df[columns_to_impute] = knn_imputer.fit_transform(df[columns_to_impute])
df = df.drop_duplicates(subset=['Title', 'Year'])

df.to_csv('movies1930_2022.csv', index=False)