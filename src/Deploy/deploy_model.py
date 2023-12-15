import os
import json 
import joblib
import hashlib
import numpy as np
import mplcyberpunk
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Set the LOKY_MAX_CPU_COUNT environment variable to the number of cores you want to use
os.environ['LOKY_MAX_CPU_COUNT'] = '4'  # Replace '4' with the desired number of cores

def get_feature_names_from_json(json_file_path):
    # Load the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Extract feature names into a list
    feature_names = data

    # Add additional names: 'year', 'budget', 'duration'
    additional_names = ['month','year', 'budget', 'duration']
    
    # Concatenate the lists
    feature_names = np.concatenate([additional_names, feature_names])

    return feature_names.tolist()  # Convert back to a regular Python list

def load_model_from_joblib(file_path):
    try:
        model = joblib.load(file_path)
        return model
    except Exception as e:
        print(f"Error loading the model from {file_path}: {e}")
        return None

def encode_categorical_features(true_features, json_filename='src/Deploy/column_names.json'):
    # Load all_features from the JSON file
    with open(json_filename, 'r') as json_file:
        all_features = json.load(json_file)

    encoded_vector = [1 if feature in true_features else 0 for feature in all_features]
    return np.array(encoded_vector)

def scale_numerical_inputs(numerical_inputs):
    # Example scaled parameters
    scaled_parameters = {
        'Year': {'mean': 2001.8869670763163, 'std': 14.084593842775673},
        'Original budget': {'mean': 34111136.278258234, 'std': 53715920.75652778},
        'Duration': {'mean': 108.96904870277652, 'std': 20.294769384770788},
    }

    scaled_values = []

    for feature in numerical_inputs:
        mean = scaled_parameters[feature]['mean']
        std = scaled_parameters[feature]['std']

        # Scale the numerical input using the local mean and std
        scaled_value = (numerical_inputs[feature] - mean) / std
        scaled_values.append(scaled_value)

    # Convert the scaled values to a NumPy array
    scaled_array = np.array(scaled_values)

    return scaled_array

def plot_budget_returns(budget_min, budget_max):
    # Assuming you have 12 months in a year
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Check if the length of the input lists matches the number of months
    if len(budget_min) != len(months) or len(budget_max) != len(months):
        raise ValueError("Number of values should match the number of months (12).")

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.style.use('cyberpunk')

    # Convert values to millions for better readability
    budget_min = np.array(budget_min) / 1e6
    budget_max = np.array(budget_max) / 1e6

    # Plot the minimum values
    plt.plot(months, budget_min, linestyle='-', label='Box Office with Minimum Budget', zorder=2)
    plt.scatter(months, budget_min, c='blue', zorder=3)

    # Plot the maximum values
    plt.plot(months, budget_max, linestyle='-', label='Box Office with Maximum Budget', zorder=2)
    plt.scatter(months, budget_max, c='orange', zorder=3)

    mplcyberpunk.make_scatter_glow()
    mplcyberpunk.add_gradient_fill(alpha_gradientglow=0.5, gradient_start='zero')
    
    # Generate a unique title using hash function and current time
    random_input = np.random.random()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    unique_title = hashlib.sha256(f"{random_input}{current_time}".encode()).hexdigest()[:8]
    
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Month")
    plt.ylabel("Total Budget Return (M$)")
    plt.legend()  # Add legend to distinguish between the two sets
    plt.grid(True)
    
    # Save the plot with the unique title
    plot_filename = f'src/graphs/plot_{unique_title}.png'
    plt.savefig(plot_filename, bbox_inches='tight')

    return plot_filename

def predict(year: int = 2023, budget: int = 30000000, duration: int = 120, Genres: [] = ['Action','Adventure'], MPAA_rating: [] = ['MPAA Rating_PG']
            , Keywords: [] = ['Keywords_Action Adventure'], Source: [] = ['Source_Original Screenplay'], 
            Production_Method: [] = ['Production method_Live Action'], 
            Creative_type: [] = ['Creative type_Contemporary Fiction'], 
            Countries: [] = ['Countries_United States']):
    
    #Numerical features
    numerical_features = {
        'Year': year,
        'Original budget': budget,
        'Duration': duration,
    }
    scaled_numerical = scale_numerical_inputs(numerical_features)
    
    #print("\nOriginal Numerical Inputs:", numerical_features)
    #print("Scaled Inputs:", scaled_numerical)

    #Categorical features
    categoriacl_features = MPAA_rating+Keywords+Source+Production_Method+Creative_type+Countries+Genres
    encoded_categorical = encode_categorical_features(categoriacl_features)
    
    #print("\nEncoded categorical: ", encoded_categorical)

    box_office_list = []

    for i in range(1,13):

        #Month
        month_vector = np.array([[i]])

        # Reshape the vectors if needed (e.g., from (3,) to (3,1))
        encoded_categorical = encoded_categorical.reshape(1, -1)
        scaled_numerical = scaled_numerical.reshape(1, -1)
        month_vector = month_vector.reshape(1,-1)

        #Input Vector
        input_vector = np.concatenate((month_vector, scaled_numerical, encoded_categorical), axis=1)
        #print(f"Input vector shape {input_vector.shape}")

        #Applying PCA
        pca = joblib.load('src/Deploy/pca_model.joblib')
        input_vector_PCA = pca.transform(input_vector)

        #Using model
        model_path = 'src/Deploy/KNN_best_model.pkl'
        loaded_model = load_model_from_joblib(model_path)

        # Now you can use the loaded_model for predictions on the input_vector
        if loaded_model is not None:
            predictions = loaded_model.predict(input_vector_PCA)
            box_office_list.append(float(predictions[0]))
            #print("Model Predictions:")
            #print(predictions)
    
    return box_office_list


def get_box_office_min_max(year: int, budget_min: int, budget_max: int, duration: int, Genres: [], MPAA_rating: [], Keywords: [], Source: [], Production_Method: [], Creative_type: [], Countries: []):
    # Call predict method for budget_min
    budget_min_values = predict(year, budget_min, duration, Genres, MPAA_rating, Keywords, Source, Production_Method, Creative_type, Countries)

    # Call predict method for budget_max
    budget_max_values = predict(year, budget_max, duration, Genres, MPAA_rating, Keywords, Source, Production_Method, Creative_type, Countries)

    file_path = plot_budget_returns(budget_min_values, budget_max_values)

    return file_path

