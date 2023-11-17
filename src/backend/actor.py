import json
from typing import Dict, List, Union
from litestar import Controller, get

from actorsAlgorithm import castingAlgorithm as cast


class Actor(Controller):
    path = "/actor"

    @get()
    async def actors_algorithm(self, budget_min: Union[float,int], 
                               budget_max: Union[float,int],
                               selected_genres: List[str] = ["Adventure"]  ) -> List[str]:
        # data = request.json
        # Access the data fields
        # budget_min = float(data['budgetMin'])
        # budget_max = float(data['budgetMax'])
        # selected_genres = data['selectedGenres']
        # selected_public = data['selectedPublic']
        # selected_goal = data['selectedGoal']
        if budget_max < budget_min:
            # return {"error": }
            raise ValueError(f"Max bugdet is low that Min buget !!! : budget_min : {budget_min} - budget_max : {budget_max}")
        
        # Validate selected genres
        for genre in selected_genres:
            if genre not in cast.get_all_genres():
                raise ValueError(f"Please select a proper genre, '{genre}' is not valid. Possible genres: {', '.join(cast.get_all_genres())}")


        budget_min = 1000
        budget_max = 10
        selected_genres = "Adventure"
        selected_public = "..."
        selected_goal = "..."


        print("i get :")
        print("budget min : ", budget_min)
        print("budget max : ", budget_max)
        print("genres : ", selected_genres)
        print("selected public : ", selected_public)
        print("selected goal : ", selected_goal)

        
        list_actor = cast.findActorsBOXOFFICE(5, selected_genres, budget_min, budget_max)
        # result = {f'actor_{i+1}': actor for i, actor in enumerate(list_actor)}

        # print(result)
        # Convert the list to a JSON string
        json_actor = json.dumps({"actors": list_actor})
        return json_actor
        
