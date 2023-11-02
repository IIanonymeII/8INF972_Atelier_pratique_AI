# -*- coding: utf-8 -*-

from sklearn.impute import SimpleImputer
import src.preprocessing.customImputer as customImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocessDataset(df, impute_strategies, cols_to_scale):
    # Create the custom imputer
    custom_imputer = customImputer.CustomImputer(strategies=impute_strategies)
    scaler = StandardScaler()
    
    # Create the ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('custom_impute', custom_imputer, list(impute_strategies.keys())),
            ('scale', scaler, cols_to_scale),
            # Add other preprocessing steps as needed
        ],
        remainder='passthrough'  # Leave other columns unchanged
    )
    
    # Add the preprocessor and the estimator to the pipeline
    preprocessing_steps = [
        ('preprocessor', preprocessor),
    ]
    
    # Create the pipeline
    pipeline = Pipeline(preprocessing_steps)
    return pipeline


custom_impute_strategies = {
    "budget": 'nearest',  # Apply 'median' imputation strategy to column 1
    # Add more columns and strategies as needed
}
cols_to_scale = ["popularity"]

#Get dataset
df = pd.read_csv('tmdb_5000_movies.csv')
column_names = df.columns
pip = preprocessDataset(df, custom_impute_strategies, cols_to_scale)
df_new = pip.fit_transform(df)
df_scaled = pd.DataFrame(df_new, columns=column_names)