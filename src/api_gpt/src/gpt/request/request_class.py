
import random
import re
from typing import List, Union
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
import requests


async def find_movie_title(type_movie: Union[str,List[str]], type_role : str = "oscar", word : str = "invention") -> str:
    if isinstance(type_movie,str):
        type_movie = [type_movie]
    
    movies = ", ".join(type_movie)
    prompt_movie = f"Crée une description de film de {movies} dans le genre {type_movie}, basée sur le mot du jour :{word}. Donne moi dans un premier temps le titre et ensuite la description du film et seulement ca. exemple Titre : ... \n Description : ..."
    conversation_style_movie = ConversationStyle.creative

    bot = await Chatbot.create()  # Passing cookies is "optional", as explained above
    response = await bot.ask(prompt=prompt_movie, conversation_style=conversation_style_movie, simplify_response=True)
    if "\n\n" in response.get("text"):
        text = response.get("text")
        # print(text)
        # print("====================")
        # Utilisez des expressions régulières pour extraire le titre et la description
        
        titre_match = re.search(r'Titre : (.+)', text)
        description_match = re.search(r'Description : (.+)', text)

        if titre_match:
            titre = titre_match.group(1).replace("*","")
        else:
            titre = "Titre non trouvé"

        if description_match:
            description = description_match.group(1).replace("*","")
        else:
            description = "Description non trouvée"




    return titre ,description


async def hazard_word():


    # Faites une requête à l'API pour obtenir un mot aléatoire
    response = requests.get("https://random-word-api.herokuapp.com/word")

    # Vérifiez si la requête a réussi
    if response.status_code == 200:
        # Le mot aléatoire est dans la réponse JSON
        mot_aleatoire = response.json()[0]
        # print("Mot aléatoire :", mot_aleatoire)
    else:
        print("Échec de la requête à l'API")
    
    return mot_aleatoire