from datetime import datetime
from flask import Flask, request, jsonify
from actorsAlgorithm import castingAlgorithm as cast
from Deploy import deploy_model as BOmodel
from flask_cors import CORS
import asyncio
import random
from api_gpt.src.gpt.request.request_class import find_movie_title, hazard_word
from backend.find_actor_image import  fetch_actor_images 
import base64
import os
from oscars_prediction.predict import predict
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
    budget_min = max(budget_min,1)
    encoded_image = None
    oscarResult = None
    if selected_goal == "Oscars":
        list_actor = cast.findActorsOSCAR(5, selected_genres, budget_min, budget_max)
        oscarResult = predict(selected_genres, [])
    else :
        list_actor = cast.findActorsBOXOFFICE(5, selected_genres, budget_min, budget_max)
        year = datetime.now().year
        year = int(year)
        duration = random.randint(90, 150)
        image_name = BOmodel.get_box_office_min_max(year, budget_min, budget_max, duration, selected_genres, [selected_public], [], [], [], [], ["Countries_United States"])
        #image_name = "src/graphs/plot.png"
        with open(image_name, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        os.remove(image_name)
    list_actor_img = fetch_actor_images(list_actor)

    word = await hazard_word() 
    title , description = await find_movie_title(type_movie=selected_genres,word=word)

    result = {"actors": list_actor,
              "img_actors":list_actor_img,
              "titre": title,
              "description":description,
              "image_bo": encoded_image,
              "oscar_result": int(oscarResult)}
    
    print(result)

    # Return the result as JSON
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)