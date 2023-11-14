from typing import Dict
from litestar import Controller, get
from api_gpt.src.gpt.request.request_class import find_movie_title,hazard_word


class ApiGpt(Controller):
    path = "/api_gpt"

    @get()
    async def list_movie(self, type_movie: str = "horror") -> Dict[str,str]:
        if type_movie not in ["horror", "comedy", "action", "drama"]:
            return {"Error": "Invalid movie type. Please choose from 'horror', 'comedy', 'action', 'drama'."}


        word = await hazard_word() 
        title ,description = await find_movie_title(type_movie=type_movie,word=word)
        print("Title:", title)
        print("\n ========= \n")
        print("Description:", description)
        
        return {"Titre":title,"Description:": description}
