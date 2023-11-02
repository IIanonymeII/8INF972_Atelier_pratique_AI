

import re
import asyncio
from src.gpt.request.request_class import find_movie_title,hazard_word


async def main():
   
    test = await hazard_word() 
    title ,description = await find_movie_title(type_movie="horror",word=test)
    print("Title:", title)
    print("\n ========= \n")
    print("Description:", description)


if __name__ == "__main__":
    asyncio.run(main())