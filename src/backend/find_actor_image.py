from typing import List, Union
import requests
from bs4 import BeautifulSoup

def fetch_wikipedia_search_results(query : str) -> Union[str, None]:
    url = f"https://fr.wikipedia.org/w/index.php?search={query}&title=Spécial%3ARecherche&profile=advanced&fulltext=1&ns0=1"
    # print(url)

    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: {response.status_code}")
        return None

def extract_search_results(query : str) -> Union[None, str]:
    search_results = fetch_wikipedia_search_results(query)

    if search_results:
        soup = BeautifulSoup(search_results, 'html.parser')
        # Finding all the search result titles
        titles = soup.find_all("li", class_="mw-search-result")

        if titles:
            try:
                search_results_list = titles[0].find("td",{"class":"searchResultImage-thumbnail"}).a.img["src"]
                url_img = "http:"+search_results_list
                # find_src = se
                return url_img
            except:
                print(f"ERROR with wikipedia img, no image found")
                return None
        else:
            print("No search results found.")
            return None
    else:
        return None



def fetch_actor_images(list_actor : List[str]) -> List[str]:
    list_actor_img = []

    for actor_name in list_actor:
        actor_name = actor_name.replace("-", "+")
        search_query = actor_name.replace(" ", "+")

        img = extract_search_results(search_query)
        if img:
            list_actor_img.append(img)
        else:
            list_actor_img.append("/pictures/Acteur1.png")  # Default image path

    return list_actor_img

