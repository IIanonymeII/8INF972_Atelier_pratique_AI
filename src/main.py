from flask import Flask, request, jsonify
from actorsAlgorithm import castingAlgorithm as cast
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
def receive_data():
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

    
    result = cast.findActorsBOXOFFICE(5, selected_genres, budget_min, budget_max)

    # Return the result as JSON
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)