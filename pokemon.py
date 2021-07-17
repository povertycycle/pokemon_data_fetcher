# import sys
import math
import os
import requests
import shutil
import json
from datetime import date, datetime

# Sets variable
TERMINAL_WIDTH = 0
MAX_CACHED_TRESHOLD = 7
STORED_POKEMON = {}
MAX_STAT = 252
ENCOUNTER_METHODS = {
    "walk": "walking on a tall grass or a cave",
    "old-rod": "fishing with an old rod",
    "good-rod": "fishing with a good rod",
    "super-rod": "fishing with a super rod",
    "surf": "surfing",
    "rock-smash": "smashing rock",
    "headbutt": "headbutt trees",
    "dark-grass": "walking in dark grass",
    "grass-spots": "walking in rustling grass",
    "cave-spots": "walking in dust clouds",
    "bridge-spots": "walking in bridge shadows",
    "super-rod-spots": "fishing in dark spots",
    "surf-spots": "surfing in dark spots",
    "yellow-flowers": "walking in yellow flowers",
    "purple-flowers": "walking in purple flowers",
    "red-flowers": "walking in red flowers",
    "rough-terrain": "walking in rough terrain",
    "gift": " receiving a gift",
    "gift-egg": "receiving an egg as a gift",
    "only-one": "a static encounter / one chance only",
    "pokeflute": "playing a pokeflute",
    "headbutt-low": "headbutting a low encounter rate tree",
    "headbutt-normal": "headbutting a normal encounter rate tree",
    "headbutt-high": "headbutting a high encounter rate tree",
    "squirt-bottle": "using a squirt bottle on a Sudowoodo",
    "wailmer-pail": "using a wailmer pail on a Sudowoodo",
    "seaweed": "surfing on a seaweed",
}


# Print full line spanning through terminal window
def print_full_lines():
    global TERMINAL_WIDTH
    print('#' * TERMINAL_WIDTH)


# Print centered text
def print_centered_text(text, separator):
    global TERMINAL_WIDTH
    print('#' + text.upper().center(TERMINAL_WIDTH - 2, separator) + '#')


# Print pokemon types
def print_pokemon_types(type_list):
    if len(type_list) == 1:
        print_centered_text(type_list[0], ' ')
    else:
        half_width = math.floor(TERMINAL_WIDTH/2-1)
        print(
            f"#{type_list[0].center(half_width, ' ').upper()}#{type_list[1].center(half_width, ' ').upper()}#")


# Print pokemon stats
def print_pokemon_stats(data):
    global TERMINAL_WIDTH
    global MAX_STAT
    text_widths = math.floor(TERMINAL_WIDTH / 8)
    bar_width = TERMINAL_WIDTH - (text_widths * 2) - 6

    print(f'# {"NAME":<{text_widths}}# {"STATS":<{text_widths}}#{"":<{bar_width}}#')
    print_full_lines()
    for i in data:
        name = i["name"]
        stat = i["base"]
        percentage = math.floor(stat / MAX_STAT * bar_width)
        print(f'# {name.upper():<{text_widths}}# {stat:<{text_widths}}# {"/"*percentage}{"":<{bar_width-percentage-1}}#')


def print_pokemon_encounter(encounters):
    global TERMINAL_WIDTH
    global ENCOUNTER_METHODS
    loc_width = math.floor(TERMINAL_WIDTH * 0.25)
    ver_width = math.floor(TERMINAL_WIDTH / 14)
    method_width = TERMINAL_WIDTH - loc_width - ver_width - 7
    chance_width = math.floor(TERMINAL_WIDTH * 0.03)
    cond_width = math.floor(TERMINAL_WIDTH / 4.75)
    min_lvl_width = math.floor(TERMINAL_WIDTH * 0.055)
    max_lvl_width = math.floor(TERMINAL_WIDTH * 0.055)
    method = method_width - cond_width - \
        chance_width - min_lvl_width - max_lvl_width - 8

    print(
        f'# {"":<{loc_width}}# {"":<{ver_width}}# {"METHODS".center(method_width, " ")}#')
    print(
        f'# {"LOCATION (KANTO)".center(loc_width, " ")}# {"VERSION".center(ver_width, " ")}###{"#" * method_width}')
    print(
        f'# {"":<{loc_width}}# {"":<{ver_width}}# {"%".center(chance_width, " ")}# '
        f'{"CONDITION".center(cond_width, " ")}# {"MIN LVL":<{min_lvl_width}}# {"MAX LVL":<{max_lvl_width}}# '
        f'{"METHOD".center(method, " ")}#')
    print_full_lines()
    for i in encounters:
        enc_loc = i["location"].replace("-", " ").replace("kanto", "").upper()
        i_c = 0
        j_c = 0
        for j in i["version"]:
            enc_ver = j['name']
            for k in j["method"]:
                conditions = ''
                for l in k["condition_values"]:
                    conditions += l["name"].replace("-", " ").upper() + " "
                print(
                    f"# {(enc_loc, '')[i_c > 0]:<{loc_width}}# {(enc_ver, '')[j_c > 0]:<{ver_width}}# "
                    f"{k['chance']:<{chance_width}}# {conditions:<{cond_width}}# "
                    f"{k['min_level']:<{min_lvl_width}}# {k['max_level']:<{max_lvl_width}}# "
                    f"{ENCOUNTER_METHODS[k['method']].upper():<{method}}#"
                )
                j_c += 1
                i_c += 1


def main():
    global STORED_POKEMON
    global TERMINAL_WIDTH
    global MAX_CACHED_TRESHOLD

    pokemon_name = ""
    # Get width.
    TERMINAL_WIDTH = shutil.get_terminal_size().columns

    # Open cached files.
    if os.path.isfile('cached_files.txt'):
        with open('cached_files.txt') as json_file:
            STORED_POKEMON = json.load(json_file)
    else:
        with open('cached_files.txt', 'w+') as json_file:
            json_file.write('{ }')
            STORED_POKEMON = {}

    while True:
        if pokemon_name == 'quit' or pokemon_name == 'exit':
            break
        pokemon_name = input(
            "Find your pokemon, or enter 'quit' or 'exit': \n").lower()

        # Title.
        print_full_lines()
        print_centered_text(pokemon_name.upper(), ' ')
        print_full_lines()

        pokemon_data = {}
        cache_age = 0
        if pokemon_name in STORED_POKEMON:
            cached_date = datetime.strptime(
                STORED_POKEMON[pokemon_name]["fetched_at"], '%m/%d/%Y')
            cache_age = (datetime.today() - cached_date).days

        # Check if data is stored in cache and is not a week old.
        if pokemon_name in STORED_POKEMON and cache_age < MAX_CACHED_TRESHOLD:
            pokemon_data = STORED_POKEMON[pokemon_name]
        else:
            # Get new fetch
            response = requests.get(
                "https://pokeapi.co/api/v2/pokemon/" + pokemon_name)
            pokemon_data = {
                "fetched_at": date.today().strftime("%m/%d/%Y")}
            if response.status_code == 200:
                # Store necessary data into pokemon data
                resp_json = response.json()
                # Get pokemon encounter list
                encounter_response = requests.get(
                    resp_json["location_area_encounters"])
                if encounter_response.status_code == 200:
                    # Store pokemon encounter
                    pokemon_data["encounter"] = []
                    for i in encounter_response.json():
                        if "kanto" in i["location_area"]["name"]:
                            enc = {
                                "location": i["location_area"]["name"],
                                "version": []
                            }
                            for version in i["version_details"]:
                                methods = []
                                for method in version["encounter_details"]:
                                    methods.append({
                                        "chance": method["chance"],
                                        "condition_values": method["condition_values"],
                                        "max_level": method["max_level"],
                                        "min_level": method["min_level"],
                                        "method": method["method"]["name"],
                                    })
                                enc["version"].append({
                                    "name": version["version"]["name"],
                                    "method": methods,
                                })

                            pokemon_data["encounter"].append(enc)

                # Pokemon index
                pokemon_data["index"] = resp_json["id"]
                # Pokemon type
                pokemon_data["types"] = []
                for i in resp_json["types"]:
                    pokemon_data["types"].append(i["type"]["name"])
                # Pokemon stats
                pokemon_data["stats"] = []
                for i in resp_json["stats"]:
                    pokemon_data["stats"].append(
                        {
                            "name": i["stat"]["name"],
                            "base": i["base_stat"]
                        }
                    )

            STORED_POKEMON[pokemon_name] = pokemon_data

            # Save cache to local data.
            with open("cached_files.txt", "w+") as f:
                json.dump(STORED_POKEMON, f)

        if pokemon_name != 'exit' and pokemon_name != 'quit':
            if len(pokemon_data) <= 1:
                print_centered_text("No pokemon named " +
                                    pokemon_name + " found.", ' ')
                print_full_lines()
            else:
                print_centered_text("#"+str(pokemon_data["index"]), ' ')
                print_full_lines()
                print_pokemon_types(pokemon_data["types"])
                print_full_lines()
                print_pokemon_stats(pokemon_data["stats"])
                print_full_lines()
                print_centered_text("ENCOUNTER", ' ')
                print_full_lines()
                print_pokemon_encounter(pokemon_data["encounter"])
                print_full_lines()


if __name__ == "__main__":
    main()
    print_centered_text("Closing Application", "#")
