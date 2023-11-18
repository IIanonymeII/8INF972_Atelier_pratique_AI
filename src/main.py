from flask import Flask, request, jsonify
from actorsAlgorithm import castingAlgorithm as cast
from flask_cors import CORS
import asyncio

from api_gpt.src.gpt.request.request_class import find_movie_title, hazard_word
from backend.find_actor_image import  fetch_actor_images 

app = Flask(__name__)
CORS(app)
# pip install asgiref



@app.route('/', methods=['POST'])
async def receive_data():
    data = request.json
    # Access the data fields
    budget_min = float(data['budgetMin'])
    budget_max = float(data['budgetMax'])
    selected_genres = data['selectedGenres']
    selected_public = data['selectedPublic']
    selected_goal = data['selectedGoal']

    print("i get :")
    print("budget min : ", budget_min)
    print("budget max : ", budget_max)
    print("genres : ", selected_genres)
    print("selected public : ", selected_public)
    print("selected goal : ", selected_goal)


    list_actor = cast.findActorsBOXOFFICE(5, selected_genres, budget_min, budget_max)
    list_actor_img = fetch_actor_images(list_actor)

    word = await hazard_word() 
    title , description = await find_movie_title(type_movie=selected_genres,word=word)

    result = {"actors": list_actor,
              "img_actors":list_actor_img,
              "titre": title,
              "description":description}

    # Return the result as JSON
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)