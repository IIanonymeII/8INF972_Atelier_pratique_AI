import pandas as pd
from sklearn.preprocessing import StandardScaler


#Get dataset
data =pd.read_csv('src/the_numbers/movies1930_2022.csv')

###################
# FEATURE SELECTION
###################

print("\n1. Feature selection")

#ALL FEATURES:
#Title,Year,Month,MPAA Rating,Original domestic B.O,Original international B.O,Adjusted domestic B.O,Adjusted international B.O,Original budget,Adjusted budget,Duration,Keywords,Source,Production method,Creative type,Companies,Countries,Languages,Genres,Action,Adventure,Animation,Comedy,Crime,Documentary,Drama,Family,Fantasy,History,Horror,Music,Mystery,Romance,Science Fiction,TV Movie,Thriller,War,Western,Total original B.O,Total adjusted B.O


features = [
    'Title','Year','Month','MPAA Rating','Adjusted domestic B.O','Adjusted international B.O','Adjusted budget','Duration','Keywords','Source','Production method','Creative type','Companies','Countries','Action','Adventure','Animation','Comedy','Crime','Documentary','Drama','Family','Fantasy','History','Horror','Music','Mystery','Romance','Science Fiction','TV Movie','Thriller','War','Western','Total adjusted B.O'
]

data = data[features]

print("Original dataset with feature selection: " + str(data.shape))

#############################################
# DATA PREPROCESSING: REMOVING MISSING VALUES 
#############################################

print("\n2. Removing missing values")

# Check for missing values in the entire dataset
print("\nMissing values for each column")
#print(data.isnull().sum())

#Removing the companies feature because it is not essential and contains the most missing values
data.drop('Companies', axis=1, inplace=True)

# Check for missing values in the entire dataset
print("\nMissing values for each column after removing companies")
#print(data.isnull().sum())

#We remove all the missing values, at most 1896 rows will be lost
data.dropna(inplace=True)

# Check for missing values in the entire dataset
print("\nMissing values for each column after removing all missing values")
#print(data.isnull().sum())
print("\nShape of dataset after handling missing values is: " + str(data.shape))

########################################
# DATA PREPROCESSING: HANDLING OUTLIERS 
########################################

print("\n3. Handling outliers")

#First we look at outliers of numerical values
#We do NOT perform scaling on the target of the model
numerical_features = [
    'Year','Adjusted domestic B.O','Adjusted international B.O','Adjusted budget','Duration'
]

#Statistics of numerical data in dataset
numerical_data = data[numerical_features]
print("\nStatistics of numerical dataset before cleaning")
#print(numerical_data.describe())

#Removing zero values in adjusted box office, adjusted international box office, adjusted box office, adjusted budget and duration

# A box office of zero, a budget of zero or a duration of zero are odd values that are removed from training

# Assuming df is your DataFrame and columns_list contains the specific columns
columns_list = ['Adjusted domestic B.O','Adjusted international B.O','Adjusted budget','Duration']  

# Remove rows where any of the specified columns have zero values in the ORIGINAL DATASET
data = data[~(data[columns_list] == 0).any(axis=1)]

#Statistics of numerical data in dataset after removing zero values
numerical_data = data[numerical_features]
print("\nStatistics of numerical dataset after cleaning")
#print(numerical_data.describe())
print("\nShape of dataset after removing zero: " + str(data.shape))

###############################################
# DATA PREPROCESSING: ENCODING CATEGORICAL DATA 
###############################################

#Perform one hot encoding on the column "keywords" and "MPAA rating"

print("\n4. Encoding categorical data")

categorical_features = [
    'MPAA Rating','Keywords','Source','Production method','Creative type','Countries'
]

for feature in categorical_features:
    unique_values_count = data[feature].nunique()
    print(f"Number of unique values in '{feature}': {unique_values_count}")

#One hot encoding of each categorical feature
data = pd.get_dummies(data, columns=categorical_features, prefix='columns_to_encode')

#Shape of dataset after onehot encoding
print("\nShape of dataset after one hot encoding: " + str(data.shape))

#################################################################
# DATA PREPROCESSING: TEXT DATA PROCESSING [POSSIBLE IMPROVEMENT]
#################################################################

#Instead of encoding the keywords using one hot encoding, we use tdidf to determine the importance
#of the keyword. 
# First we remove the stop words such as: a, the, in then we determine how useful a a keyword is

######################################
# DATA PREPROCESSING: FEATURE SCALING 
######################################

#Perform one hot encoding on the column "keywords"

print("\n5. Feature scaling")

print("\nStatistics of numerical dataset before scaling")
#print(data[numerical_features].describe())

# Standard Scaling
standard_scaler = StandardScaler()
data[numerical_features] = standard_scaler.fit_transform(data[numerical_features])

print("\nStatistics of numerical dataset after cleaning")
#print(data[numerical_features].describe())

###########################################################################################################
# DATA PREPROCESSING: FEATURE ENGINEERING => PROFITABILITY OF A MOVIE BUDGET/REVENUE [POSSIBLE IMPROVEMENT]
###########################################################################################################

##################################################
# SAVING DATAFRAME INTO NEW CSV FILE FOR TRAINING
##################################################

print("\n6. Saving dataframe into new csv file")

print("\nShape of dataset: " + str(data.shape))

data.to_csv('dataset.csv', index=False)