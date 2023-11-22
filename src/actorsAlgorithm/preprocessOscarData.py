#AUTHOR : Diane Lantran
import pandas as pd
import os
import chardet

#################
### CONSTANTS ###
#################
file_path = os.path.abspath(__file__)
file_directory = os.path.dirname(file_path)
current_directory = os.path.dirname(os.path.dirname(file_directory))
desired_categoriesGG = [
    'Best Performance by an Actress in a Limited Series or a Motion Picture Made for Television',
    'Best Performance by an Actor in a Limited Series or a Motion Picture Made for Television',
    'Actress In A Supporting Role - Series Or Television Movie',
    'Actress In A Leading Role - Drama Series Or Television Movie',
    'Actor In A Leading Role - Drama Series Or Television Movie','Actor In A Leading Role - Musical Or Comedy Series Or Television Movie','Actor In A Supporting Role - Series Or Television Movie', 'Actress In A Leading Role - Musical Or Comedy Series Or Television Movie','Best Performance by an Actress in a Motion Picture - Musical or Comedy', 'Best Performance by an Actress in a Supporting Role in a Series, Limited Series or Motion Picture Made for Television',      
'Best Performance by an Actor in a Supporting Role in a Series',
'Limited Series or Motion Picture Made for Television',        
'Actor In A Television Series - Musical Or Comedy',
'Actor In A Television Series - Drama',
'Actress In A Television Series - Drama',
'Actress In A Television Series - Musical Or Comedy',
'Best Performance by an Actress In A Television Series - Drama',
'Best Performance by an Actor In A Television Series - Drama',
'Best Performance by an Actress in a Television Series - Musical or Comedy',
'Best Performance by an Actor in a Television Series - Musical or Comedy',
'Actor In A Supporting Role - Television Series',
'Actress In A Supporting Role - Television Series',
'Actor In A Television Series' 'Actress In A Television Series',
'New Foreign Star Of The Year - Actress',
'New Foreign Star Of The Year - Actor' 'Foreign Film - Foreign Language',
'Best Performance by an Actress in a Motion Picture - Drama',
'Best Performance by an Actor in a Motion Picture - Drama',
'Best Performance by an Actor in a Motion Picture - Musical or Comedy',
'New Star Of The Year' 'Actress In A Leading Role - Musical Or Comedy',
'Samuel Goldwyn International Award' 'Famous Silent Filmstars',
'New Star Of The Year - Actress',
'New Star Of The Year - Actor' 'Juvenile Performance' 'Cinematography',
'Foreign Film - English Language',
'Best Motion Picture - Foreign Language',
'Actress In A Leading Role',
'Actor In A Leading Role',
'Best Performance by an Actress in a Supporting Role in any Motion Picture',
'Best Performance by an Actor in a Supporting Role in any Motion Picture'

]

##############
###DATASETS###
##############
#golden globes dataset
gg_file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'golden_globe_awards.csv')
gg_data = pd.read_csv(gg_file_path, encoding='ISO-8859-1', sep=',')
#BAFTA dataset
bafta_file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'bafta_films.csv')
bafta_data = pd.read_csv(bafta_file_path, encoding='ISO-8859-1', sep=',')
#BAFTA dataset
sag_file_path = os.path.join(current_directory, 'src', 'Kaggle_dataset', 'screen_actor_guild_awards.csv')
sag_data = pd.read_csv(sag_file_path, encoding='ISO-8859-1', sep=',')


###############
###ALGORITHM###
###############
def cleanGG():
    gg_data_filtered = gg_data[gg_data['category'].isin(desired_categoriesGG)]
    gg_data_filtered = gg_data_filtered.dropna(subset=['nominee', 'category', 'win'])
    gg_data_filtered = gg_data[['nominee', 'win']]
    gg_data_filtered.to_csv(gg_file_path)

def cleanBafta():
    bafta_data_filtered = bafta_data.dropna(subset=['nominee', 'category', 'winner'])
    bafta_data_filtered = bafta_data_filtered[bafta_data_filtered['category'].str.contains('Actor|Actress|Promising Newcomer To Leading Film Roles')]
    bafta_data_filtered = bafta_data_filtered[['nominee', 'winner']]
    bafta_data_filtered.to_csv(bafta_file_path)

def cleanSAG():
    sag_data_filtered = sag_data[['full_name', 'won']]
    sag_data_filtered = sag_data_filtered.dropna()
    sag_data_filtered['full_name'] = sag_data_filtered['full_name'].str.title() #capital letters deleted
    sag_data_filtered.to_csv(sag_file_path)

def cleanDataSets():
    #cleanGG()
    #cleanBafta()
    cleanSAG()

def mergeDataSets():
    merged_data = pd.merge(gg_data, bafta_data, on='nominee', how='outer', suffixes=('_GG', '_BAFTA'))
    merged_data = pd.merge(merged_data, sag_data, left_on='nominee', right_on='full_name', how='outer')
    merged_data = merged_data.fillna(False)
    merged_data['WinGG'] = merged_data['win'] == True
    merged_data['WinBAFTA'] = merged_data['winner'] == True
    merged_data['WinSAG'] = merged_data['won'] == True
    final_dataset = merged_data[['nominee', 'WinGG', 'WinBAFTA', 'WinSAG']]
    #filtre les doublons si un acteur a été nominé plusieurs fois
    grouped_data = final_dataset.groupby('nominee', as_index=False).agg({
    'WinGG': 'max',
    'WinBAFTA': 'max',
    'WinSAG': 'max'
})
    grouped_data.to_csv('src/actorsAlgorithm/recompense_data.csv')

def addRecScore():
    file_path = os.path.join(current_directory, 'src', 'actorsAlgorithm', 'recompense_data.csv')
    recompense_data = pd.read_csv(file_path, encoding='ISO-8859-1', sep=',')
    recScores = []

    for index, row in recompense_data.iterrows():
        score = 0
        if row['WinGG']:
            score += 1
        if row['WinBAFTA']:
            score += 1
        if row['WinSAG']:
            score += 1
        recScores.append(score)

    recompense_data['Score'] = recScores
    recompense_data.to_csv('src/actorsAlgorithm/recompense_data.csv', index=False)


##########
###TEST###
##########
#cleanDataSets()
#mergeDataSets()
#addRecScore()