
import re
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle


async def find_movie_title(type_movie: str) -> str:
    result: str = ""
    prompt_movie = f"Génère une description de film imaginaire dans le genre {type_movie} , sans référence à des films existants et sans considération pour l'actualité. Il faut que le film soit plutot orienté pour avoir des oscars donc un film d'horreur mais aussi un peu d'auteur"
    conversation_style_movie = ConversationStyle.creative

    bot = await Chatbot.create()  # Passing cookies is "optional", as explained above
    response = await bot.ask(prompt=prompt_movie, conversation_style=conversation_style_movie, simplify_response=True)
    if "\n\n" in response.get("text"):
        print(response)
        text = response.get("text")
        # Define regular expression patterns
        pattern_title = r'\*\*(.*?)\*\*'
        pattern_description = r'\*\*\n\n(.*?)$'

        # Use re.search() to find the title
        title_match = re.search(pattern_title, text)
        if title_match:
            title = title_match.group(1)
        else:
            title = "No title found"

        # Use re.search() to find the description
        description_match = re.search(pattern_description, text)
        if description_match:
            description = description_match.group(1)
        else:
            description = "No description found"
        print("Title:", title)
        print("Description:", description)

    else:
        print("================ ERROR ================")
        print(response.get("text"))

    return result
