#AUTHOR : Diane Lantran
import pandas as pd
import os
import random
from flask import jsonify

################
### DATASETS ###
################
file_path = os.path.abspath(__file__)
file_directory = os.path.dirname(file_path)
current_directory = os.path.dirname(os.path.dirname(file_directory))

# movie dataset
file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'tmdb_5000_movies.csv')
movie_data = pd.read_csv(file_path)
# credit dataset
file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'tmdb_5000_credits.csv')
credits_data = pd.read_csv(file_path)
# actor score generated dataset
file_path = os.path.join(current_directory, 'src', 'actorsAlgorithm', 'popularity_data.csv')
popularity_data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',')
# oscar dataset
file_path = os.path.join(current_directory, 'src', 'actorsAlgorithm', 'recompense_data.csv')
recompense_data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',')


#################
### ALGORITHM ###
#################
def  findActorsBOXOFFICE(castSize, genres, budgetMin, budgetMax):
    # castSize : nombre d'acteurs à retourner
    # genres : liste des genres selectionnés par l'utilisateur
    # budgetMin / budgetMax : selection par le slider

    candidates = getActorGenre(genres)
    [minActorSalary, maxActorSalary] = getSalaryBudget(castSize, genres, budgetMin, budgetMax) #la proportion du budget allouée aux salaire varie en fonction du genre et du budget voulu
    candidates = filterCandidates(candidates, minActorSalary, maxActorSalary) #filtre par le salaire & classe par ordre de popularité
   
    #retourne les castSize premiers
    print(candidates)
    if candidates is not None :
        #random sur les castSize*2 premiers pour ne pas retourner toujours les mêmes
        if len(candidates)>2*castSize:
            candidates = candidates[:2*castSize]
            random.shuffle(candidates)
        random_candidates = candidates[:castSize]
        return random_candidates
    else :
        return None

def findActorsOSCAR(castSize, genres, budgetMin, budgetMax):
    # castSize : nombre d'acteurs à retourner
    # genres : liste des genres selectionnés par l'utilisateur
    # budgetMin / budgetMax : selection par le slider

    candidates = getActorGenre(genres)
    [minActorSalary, maxActorSalary] = getSalaryBudget(castSize, genres, budgetMin, budgetMax)
    candidates = filterCandidates(candidates, minActorSalary, maxActorSalary)

    rec_candidates = []

    # filtrage OSCAR
    for actor in candidates:
        if actor in recompense_data['nominee'].values:
            score = recompense_data.loc[recompense_data['nominee'] == actor, 'Score'].values[0]
            rec_candidates.append({'Actor': actor, 'Score': score})

    rec_candidates = pd.DataFrame(rec_candidates)
    rec_candidates = rec_candidates.sort_values(by='Score', ascending=False)
    list_rec_candidates = rec_candidates['Actor'].tolist()

    # retourne les castSize premiers
    print("candidates rec : ", list_rec_candidates)
    if list_rec_candidates:
        # random sur les castSize*2 premiers pour ne pas retourner toujours les mêmes
        if len(list_rec_candidates) > 2 * castSize:
            list_rec_candidates = random.sample(list_rec_candidates[:2*castSize], castSize)
        list_rec_candidates = list_rec_candidates[:castSize]
        return list_rec_candidates
    elif not list_rec_candidates:
        if len(candidates) > 2 * castSize:
            candidates = random.sample(candidates[2*castSize], castSize)
        candidates = candidates[:castSize]
        return candidates
    else:
        return None

def getActorGenre(genres):
    print("genres for candidates: ", genres)
    threshold = 0.7 #i want 70% of matching genres
    similarMovies = get_movies_by_genres(genres, threshold)
    similarMoviesActors = getActorsFromMovies(similarMovies)
    return(similarMoviesActors)

def get_movies_by_genres(genres, threshold):
    matching_movies = []
    for index, row in movie_data.iterrows():
        movie_genres = [genre['name'] for genre in eval(row['genres'])]
        matching_percentage = sum(genre in movie_genres for genre in genres) / len(genres)
        if matching_percentage >= threshold:
            matching_movies.append(row['original_title'])
    if (len(matching_movies) == 0 and threshold > 0) :
        threshold = threshold -0.1
        return get_movies_by_genres(genres, threshold)
    else :
        return matching_movies
    
def get_all_genres():
    all_genres = []
    for index, row in movie_data.iterrows():
        movie_genres = [genre['name'] for genre in eval(row['genres'])]
        all_genres.extend(movie_genres)
    return list(set(all_genres)) # unique list

def getActorsFromMovies(similarMovies):
    actors = []
    for movie in similarMovies:
        credits_row = credits_data[credits_data['title'] == movie]
        if not credits_row.empty:
            # Extract the cast information
            cast_info = eval(credits_row['cast'].iloc[0])
            actors.extend([actor['name'] for actor in cast_info])
    return(actors)

def getSalaryBudget(castSize, genres, budgetMin, budgetMax):
    coef = 1.7 #les chiffres utilisés ont été recueillis d'après une étude du CNC sur des films francais
    #nous utilisons un coefficient multiplicateur correspondant à l'ecart de budget entre films americains et francais
    if ('Documentaire' and 'Animation' in genres):
        proportion = coef*(0.04+0.13)/2
    elif ('Animation' in genres):
        proportion = coef*0.13
    elif ('Documentaire' in genres):
        proportion = coef*0.04        
    else:
        proportion = coef*0.1
    min = budgetMin*proportion/castSize
    max = budgetMax*proportion/castSize
    salaryBudget = [min, max]    
    return(salaryBudget) 

def filterCandidates(candidates, minActorSalary, maxActorSalary):
    popularity_data_filtered = popularity_data[
        (popularity_data['Actor'].isin(candidates)) &
        (minActorSalary < popularity_data['EstimatedIncome'] * 1000000) &
        (popularity_data['EstimatedIncome'] * 1000000 < maxActorSalary)
    ]

    sortedCandidates = popularity_data_filtered.sort_values(by='Score', ascending=False)
    result = list(sortedCandidates['Actor'])
    return result


