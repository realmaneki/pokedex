import os
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

def get_pokemon_info(pokemon_name):
    pokemon_name = pokemon_name.replace("'", "")
    pokemon_name = pokemon_name.replace(". ", "-")
    pokemon_name = pokemon_name.replace("♀", "-f")
    pokemon_name = pokemon_name.replace("♂", "-m")
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)
    return response.json()

def get_pokemon_image(pokemon_info):
    return pokemon_info["sprites"]["front_default"]

def get_pokemon_types(pokemon_info):
    return [item["type"]["name"] for item in pokemon_info["types"]]


def scrap_pokemon_list():
    url = "https://pokemondb.net/pokedex/game/lets-go-pikachu-eevee"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    pokemon_list = []
    cards_list = soup.find("div", class_="infocard-list")
    cards_data = cards_list.find_all("span", class_="infocard-lg-data")

    for data in cards_data:
        poke_name = data.find("a").get_text()
        poke_no = data.find("small").get_text()
        pokemon_list.append((poke_name, poke_no))

    return pokemon_list

pokemon_list = scrap_pokemon_list()
#print(pokemon_list)

pdf = FPDF(format="A5")
pdf.add_font("DejaVu", "", "pokedex/DejaVuSans.ttf", uni=True) # In case of opening from a folder that is not in another folder, change the path to "DejaVuSans.ttf" only

tmp_dir = "tmp_poke_imgs"
os.makedirs(tmp_dir, exist_ok=True)

for pokemon_name, pokemon_no in pokemon_list:
    try:
        info = get_pokemon_info(pokemon_name)
        image_url = get_pokemon_image(info)

        img_path = os.path.join(tmp_dir, f"{pokemon_no.strip('#')}_{pokemon_name}.png".replace(" ", "_"))
        img_bytes = requests.get(image_url, timeout=10).content
        with open(img_path, "wb") as f:
            f.write(img_bytes)
        types = get_pokemon_types(info)

        pdf.add_page()
        pdf.set_font("DejaVu", size=16)
        pdf.text(x=5, y=10, txt=f"{pokemon_no} {pokemon_name}")

        pdf.image(img_path, x=30, y=15, w=50, h=50)

        pdf.set_font("DejaVu", size=12)
        pdf.text(x=5, y=80, txt=f"Typ: {', '.join(types)}")
    except Exception as e:
        print("Error for:" , pokemon_name, "|", e)
pdf.output("pokedex.pdf")
