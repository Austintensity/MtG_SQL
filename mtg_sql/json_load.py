#  2021  Paul Austin
# Thanks to https://scryfall.com/docs/api
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
import time
import os
from pathlib import Path
import mtg_sql
import mtg_regex


def fix_text(oracletext):
    """replace Unicode '\u2212' character that Python's console can't print, as well as a few other gnarly characters
    Returns: String 'card_string'  """
    card_string = oracletext.replace('−', '-')
    card_string = card_string.replace('\n', '     ')    
    card_string = card_string.replace("ö", "o")
    card_string = card_string.replace("Ã¶", "o")
    card_string = card_string.replace("Ã¢", "a")
    card_string = card_string.replace("û", "u")
    card_string = card_string.replace("Ã»", "u")
    return card_string


def single_sided_card_json(the_card):
    """ Used for processing JSON data for cards of the following layouts:
    'normal' , 'token' ,  'meld'  ,  'saga' ,    'leveler' ,    'host' ,'augment',    'emblem'
    Parameter:  the_card: Card object in JSON format from https://scryfall.com/docs/api/bulk-data
    Returns: nothing  , RUNS insert_card_from_json() to add to 'Grandtable' and 'Grandtable_Condensed' tables
    Fetches  name, colors, color_identity, mana_cost, cmc, card type, oracle text, keywords, power, toughness, loyalty,
    rarity, image uris (urls?)"""

    face1_name = the_card['name']
    face1_type = the_card['type_line']
    face1_text = fix_text(the_card['oracle_text'])
    face1_manacost = str(the_card['mana_cost'])
    face1_cmc = the_card['cmc']
    face1_rarity = the_card['rarity']
    face1_colours = the_card['colors']
    if not face1_colours:
        face1_colours.append('C')
    face1_colours = str(face1_colours)
    face1_colour_id = the_card['color_identity']
    if not face1_colour_id:
        face1_colour_id.append('C')
    face1_colour_id = str(face1_colour_id)
    
    try:
        face1_images = the_card['image_uris']['normal']
    finally:
        face1_images = mtg_regex.regex_get_image(str(the_card.__dict__.items()))
    try:
        if 'creature' in face1_type.lower():
            face1_power = the_card['power']
            face1_toughness = the_card['toughness']
        else:
            face1_power = "N/A"
            face1_toughness = "N/A"
    finally:
        if face1_name == "B.F.M. (Big Furry Monster)":
            # A unique creature card from the Unglued set. Left side 'Melds' witb Right side to make a 99/99
            face1_power = "See: other half"
            face1_toughness = "See: other half"
        else:
            print("encountered exception attempting to access ", face1_name,
                  " power/toughness  - single_sided_card_json")
            face1_power = "N/A"
            face1_toughness = "N/A"
        
    try:    
        if 'planeswalker' in face1_type.lower():
            face1_loyalty = the_card['loyalty']
        else:
            face1_loyalty = "N/A"
    finally:
        face1_loyalty = "N/A"
        print(face1_name, " isn't finding ['loyalty'] - single_sided_card_json")
        
    try:
        face1_keywords = str(the_card['keywords'])
        if not face1_keywords:
            face1_keywords = ''
    finally:
        face1_keywords = "[]"
        print(face1_name, " isn't finding ['keywords'] - single_sided_card_json")
    
    mtg_sql.insert_card_from_json(face1_name, face1_colours, face1_colour_id, face1_manacost, face1_cmc, face1_type,
                                  face1_text, face1_keywords, face1_power, face1_toughness, face1_loyalty,
                                  face1_rarity, face1_images)

    mtg_sql.insert_cardref(face1_name, "Cards_Condensed")


def split_card_json(the_card):
    """ Used for processing JSON data for cards of the following layouts:
    'split' , 'flip' ,  'adventure'
    Parameter:  the_card: Card object in JSON format from https://scryfall.com/docs/api/bulk-data    
    Returns: nothing  , RUNS insert_splitcard_from_JSON() to add to 'GrandtableSplit' and
    'GrandtableSplit_Condensed' tables
    Fetches  names, colors, color_identity, mana_costs, cmcs, card types, oracle texts, keywords, powers, toughness',
    loyalty's, raritys, image uris (urls?)
    RUNS regex_get_cmc() on both faces - flip cards will have one mana cost, split and adventure cards will have 2
    most data will be specific to the card, Oracle Text is specific to card faces object"""
    
    card1 = the_card['card_faces'][0]
    card2 = the_card['card_faces'][1]
    face1_layout = the_card['layout']
    face1_colours = str(the_card['colors'])
    face1_colour_id = str(the_card['color_identity'])
    face1_manacost = str(card1['mana_cost'])
    face2_manacost = str(card2['mana_cost'])    
    face1_rarity = the_card['rarity']
    face1_images = the_card['image_uris']['normal']
    face1_name = the_card['name'].partition(" // ")[0]
    face2_name = the_card['name'].partition(" // ")[2]
    face1_type = the_card['type_line'].partition(" // ")[0]
    face2_type = the_card['type_line'].partition(" // ")[2]
    face1_keywords = the_card['keywords']
    """Keywords are assigned to the whole card """    

    face1_text = fix_text(card1['oracle_text'])
    face2_text = fix_text(card2['oracle_text'])
    face1_cmc = mtg_regex.regex_get_cmc(face1_manacost)
    face2_cmc = mtg_regex.regex_get_cmc(face2_manacost)

    try:
        face1_keywords = str(the_card['keywords'])
        if not face1_keywords:
            face1_keywords = ''
    finally:
        face1_keywords = "[]"
        print("Exception encountered searching for 'keywords' - split_card_json")
        
    """Handling Creature and Planeswalker stats, if applicable """
    if "creature" in face1_type.lower():
        try:
            face1_power = card1['power']
            face1_toughness = card1['toughness']
        finally:
            print("Encountered exception attempting to access ", face1_name,
                  "'s power/toughness - split_card_json (face 1)")
            face1_power = "-"
            face1_toughness = "-"    
    else:
        face1_power = "-"
        face1_toughness = "-"

    if "creature" in face2_type.lower():    
        try:
            face2_power = card2['power']
            face2_toughness = card2['toughness']
        finally:
            print("Encountered exception attempting to access ", face2_name,
                  "'s power/toughness - split_card_json (face 2)")
            face2_power = "-"
            face2_toughness = "-"
    else:        
        face2_power = "-"
        face2_toughness = "-"

    face1_loyalty = "-"
    face2_loyalty = "-"
    # This next section is only needed if a Planeswalker ends up on a split card, I'd kinda like to see that..
    # if 'planeswalker' in face1_type.lower():    
    #     try:
    #         face1_loyalty = the_card['loyalty']
    #     finally:
    #         print ("encountered exception accessing ", face1_name, face1_type.lower(),
    #         "  (face1)  loyalty - split_card_json")
    #         face1_loyalty = "-"
    # else: face1_loyalty = "-"
    # 
    # if 'planeswalker' in face2_type.lower():    
    #     try:
    #         face2_loyalty = the_card['loyalty']
    #     finally:
    #         face2_loyalty = "-"
    # else:
    #     print ("encountered exception accessing ", face2_name, face2_type.lower(),
    #     " (face2) loyalty - split_card_json")
    #     face2_loyalty = "-"

    """Adding to SQL tables: 'GrandtableSplit' and/or 'GrandtableSplit_Condensed'"""        
    mtg_sql.insert_splitcard_from_JSON(face1_name, face2_name, face1_layout, face1_colours, face1_colour_id,
                                       face1_manacost, face1_cmc, face1_type, face1_text, face1_keywords, face1_power,
                                       face1_toughness, face1_loyalty, face1_rarity, face1_images)
    mtg_sql.insert_splitcard_from_JSON(face2_name, face1_name, face1_layout, face1_colours, face1_colour_id,
                                       face2_manacost, face2_cmc, face2_type, face2_text, face1_keywords, face2_power,
                                       face2_toughness, face2_loyalty, face1_rarity, face1_images)

    add_this = face1_name + " // " + face2_name
    mtg_sql.insert_cardref(add_this, "Face_Cards_Condensed")


def double_faced_card_json(the_card):
    """ Used for processing JSON data for cards of the following layouts:
    'transform' , 'modal_dfc' ,  'double_faced_token' , 'double_sided'
    Parameter:  the_card: Card object in JSON format from https://scryfall.com/docs/api/bulk-data
    Returns: nothing  , RUNS insert_splitcard_from_JSON() to add to 'GrandtableSplit' and 'GrandtableSplit_Condensed'
    tables (like Split_Card)
    Fetches  names, colors, color_identity, mana_costs, cmcs, card types, oracle texts, keywords, powers, toughness',
    loyalty's, raritys, image uris (urls?)
    RUNS regex_get_cmc() on both faces  - transform cards will only have 1 mana cost
    most data will be specific to the card, Oracle Text is specific to card faces object """
    
    face1_layout = the_card['layout']  # there is only one layout for the card, but named in face1_layout
    face1_colour_id = str(the_card['color_identity'])
    face1_rarity = the_card['rarity']
    face1_name = the_card['name'].partition(" // ")[0]
    face2_name = the_card['name'].partition(" // ")[2]
    card1 = the_card['card_faces'][0]
    card2 = the_card['card_faces'][1]
    face1_type = card1['type_line']
    face2_type = card2['type_line']
    face1_text = fix_text(card1['oracle_text'])
    face2_text = fix_text(card2['oracle_text'])
    face1_colours = str(card1['colors'])
    face2_colours = str(card2['colors'])
    face1_manacost = str(card1['mana_cost'])
    face2_manacost = str(card2['mana_cost'])
    face1_cmc = mtg_regex.regex_get_cmc(face1_manacost)
    face2_cmc = mtg_regex.regex_get_cmc(face2_manacost)
    face1_images = card1['image_uris']['normal']
    face2_images = card2['image_uris']['normal']
    try:
        face1_keywords = str(the_card['keywords'])
        if not face1_keywords:
            face1_keywords = ''
    finally:
        face1_keywords = "[]"
        print("Exception encountered searching for 'keywords' - double_faced_card_json")
    if "creature" in face1_type.lower():
        try:
            face1_power = card1['power']
            face1_toughness = card1['toughness']
        finally:
            print("Encountered exception attempting to access ", face1_name,
                  " power/toughness (side 1) - double_faced_card_json")
            face1_power = "-"
            face1_toughness = "-"
    else:
        face1_power = "-"
        face1_toughness = "-"
        
    if "creature" in face2_type.lower():
        try:            
            face2_power = card2['power']
            face2_toughness = card2['toughness']
        finally:
            face2_power = "-"
            face2_toughness = "-"
            print("Encountered exception attempting to access ", face2_name,
                  " power/toughness  (side 2) - double_faced_card_json")
    else:
        face2_power = "-"
        face2_toughness = "-"
        
    if 'planeswalker' in face1_type.lower():
        try:
            face1_loyalty = card1['loyalty']
        finally:
            face1_loyalty = "-"
            print("Encountered exception attempting to access ", face1_name, "'s loyalty - double_faced_card_json")
    else:
        face1_loyalty = "-"
            
    if 'planeswalker' in face2_type.lower():
        if 'planeswalker' in face1_type.lower():
            # Both sides of card are Planeswalkers and share the same Loyalty counters
            try:
                face2_loyalty = card1['loyalty']
            finally:
                face2_loyalty = "-"
                print("Encountered exception attempting to access ", face2_name, "'s loyalty - double_faced_card_json")
        else:
            # Only side 2 of the card is a Planeswalker, so card2['loyalty'] should be valid..?
            try:
                face2_loyalty = card2['loyalty']
            finally:
                face2_loyalty = "-"
                print("Encountered exception attempting to access ", face2_name, "'s loyalty - double_faced_card_json")
                
    else:
        face2_loyalty = "-"

    # Adding to SQL tables: 'GrandtableSplit' and/or 'GrandtableSplit_Condensed'
    mtg_sql.insert_splitcard_from_JSON(face1_name, face2_name, face1_layout, face1_colours, face1_colour_id, 
                                       face1_manacost, face1_cmc, face1_type, face1_text, face1_keywords, face1_power, 
                                       face1_toughness, face1_loyalty, face1_rarity, face1_images)
    
    mtg_sql.insert_splitcard_from_JSON(face2_name, face1_name, face1_layout, face2_colours, face1_colour_id, 
                                       face2_manacost, face2_cmc, face2_type, face2_text, face1_keywords, face2_power, 
                                       face2_toughness, face2_loyalty, face1_rarity, face1_images)

    add_this = face1_name + " // " + face2_name
    # Add the full card name to the Cardref table
    mtg_sql.insert_cardref(add_this, "Face_Cards_Condensed")    


def ignore_card_json(the_card):
    """planar, art series, scheme and the other obscure card types are just ignored"""
    # ignored_counter = ignored_counter + 1
    # print ("Skipped card:",the_card['name'], ": ", the_card['layout'])
    pass


convert_layout_json = {
    'normal': single_sided_card_json,
    'meld': single_sided_card_json,
    'saga': single_sided_card_json,
    'class': single_sided_card_json,
    'leveler': single_sided_card_json,
    'host': single_sided_card_json,
    'augment': single_sided_card_json,
    'emblem': single_sided_card_json,
    'split': split_card_json,
    'flip': split_card_json,
    'adventure': split_card_json,
    'transform': double_faced_card_json,
    'modal_dfc': double_faced_card_json,
    'double_sided': double_faced_card_json,
    'token': ignore_card_json,
    'double_faced_token': ignore_card_json,
    'planar': ignore_card_json,
    'art_series': ignore_card_json,
    'scheme': ignore_card_json,
    'vanguard': ignore_card_json
}


def select_case_layout_json(layout, the_card):
    """The layout will determine which table the card gets added to
    called by main()"""
    execute_function = convert_layout_json.get(layout, "Invalid type")
    return execute_function(the_card)


def main():
    """ Adds all items from the specified JSON file into the Grandtable, GrandtableCondensed, GrandtableSplit, and
    GrandtableSplitCondensed
    Timed process: August 18: 6min 28sec   """
    begin_time = time.time()
    print(time.localtime(begin_time))
    current_folder = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
    root_folder = Path(current_folder).parent
    data_folder = root_folder / "db"
    latest_card_json = data_folder / "all-cards-20210818091127.json"
    counter = 0
    # latest_card_json = data_folder / 'all-cards-20210818091127.json'  # Current full database,
    # check https://scryfall.com/docs/api/bulk-data for latest version

    mtg_sql.cur.execute("DROP TABLE IF EXISTS 'CardRef'")
    mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Grandtable'")
    mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableCondensed'")
    mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableSplit'")
    mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableSplitCondensed'")
    mtg_sql.check_all_tables()
    with open(latest_card_json, encoding='utf-8') as f:
        data = json.load(f)
    for card in data:
        if card['lang'] == "en":
            try:        
                counter += 1
                select_case_layout_json(card['layout'], card)
            except Exception as e:
                counter -= 1
                print("Encountered exception accessing ", card['name'], " - main import", e)
    print(counter, " records found")
    end_time = time.time()
    run_time = end_time - begin_time
    print(time.localtime(end_time))
    print("Runtime: ", round(run_time, 3), " seconds")
    # latest_card_json.close()


if __name__ == '__main__':
    main()
