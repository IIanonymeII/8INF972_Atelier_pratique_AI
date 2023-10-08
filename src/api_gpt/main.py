

import re
import asyncio
from src.gpt.request.request_class import find_movie_title


test = asyncio.run(find_movie_title(type_movie="horreur"))
