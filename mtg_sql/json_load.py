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
import sqlite3
import os
import re
from pathlib import Path
import mtg_sql
import mtg_regex
import mtg_main

def fix_text(oracletext):
    """replace Unicode '\u2212' character that Python's console can't print, as well as a few other gnarly characters
    Returns: String 'card_string'  """
    card_string = oracletext.replace('−', '-')
    card_string = card_string.replace('\n', '     ')    
    card_string = card_string.replace("ö","o")
    card_string = card_string.replace("Ã¶","o")
    card_string = card_string.replace("Ã¢","a")
    card_string = card_string.replace("û","u")
    card_string = card_string.replace("Ã»","u")
    return card_string

def Single_Sided_Card_JSON(the_card):
    """ Used for processing JSON data for cards of the following layouts:
    'normal' , 'token' ,  'meld'  ,  'saga' ,    'leveler' ,    'host' ,'augment',    'emblem'
    Parameter:  the_card : Card object in JSON format from https://scryfall.com/docs/api/bulk-data
    Returns: nothing  , RUNS insert_card_from_JSON() to add to 'Grandtable' and 'Grandtable_Condensed' tables
    Fetches  name, colors, color_identity, mana_cost, cmc, card type, oracle text, keywords, power, toughness, loyalty,
    rarity, image uris (urls?)"""

    face1_name = the_card['name']
    face1_type = the_card['type_line']
    face1_text = fix_text(the_card['oracle_text'])
    face1_manacost = str(the_card['mana_cost'])
    face1_cmc = the_card['cmc']
    face1_rarity = the_card['rarity']
    face1_colours = the_card['colors']
    if not face1_colours : face1_colours.append ('C')
    face1_colours = str(face1_colours)
    face1_colourID = the_card['color_identity']
    if not face1_colourID : face1_colourID.append ('C')
    face1_colourID = str(face1_colourID)
    
    try:
        face1_images = the_card['image_uris']['normal']
    except:
        face1_images = mtg_regex.regex_get_image(str(the_card.__dict__.items()))
    try:
        if 'creature' in face1_type.lower():
            face1_power = the_card['power']
            face1_toughness = the_card['toughness']
        else:
            face1_power = "N/A"
            face1_toughness = "N/A"
    except:
        if face1_name == "B.F.M. (Big Furry Monster)":
            ## A unique creature card from the Unglued set. Left side 'Melds' witb Right side to make a 99/99
            face1_power = "See: other half"
            face1_toughness = "See: other half"
        else:
            print ("encountered exception attempting to access ",face1_name , " power/toughness  - Single_Sided_Card_JSON")
            face1_power = "N/A"
            face1_toughness = "N/A"
        
    try:    
        if 'planeswalker' in face1_type.lower():
            face1_loyalty = the_card['loyalty']
        else:
            face1_loyalty = "N/A"
    except:
        face1_loyalty = "N/A"
        print (face1_name, " isn't finding ['loyalty'] - Single_Sided_Card_JSON")
        
    try:
        face1_keywords = str(the_card['keywords'])
        if not face1_keywords : face1_keywords.append (' ')
    except:
        face1_keywords = "[]"
        print (face1_name, " isn't finding ['keywords'] - Single_Sided_Card_JSON")
    
    mtg_sql.insert_card_from_JSON(face1_name, face1_colours, face1_colourID, face1_manacost, face1_cmc, face1_type, face1_text,
                          face1_keywords, face1_power, face1_toughness, face1_loyalty, face1_rarity, face1_images)

    mtg_sql.insert_cardref(face1_name, "Cards_Condensed")

def Split_Card_JSON(the_card):
    """ Used for processing JSON data for cards of the following layouts:
    'split' , 'flip' ,  'adventure'
    Parameter:  the_card : Card object in JSON format from https://scryfall.com/docs/api/bulk-data    
    Returns: nothing  , RUNS insert_splitcard_from_JSON() to add to 'GrandtableSplit' and 'GrandtableSplit_Condensed' tables
    Fetches  names, colors, color_identity, mana_costs, cmcs, card types, oracle texts, keywords, powers, toughness', loyalty's,
    raritys, image uris (urls?)
    RUNS regex_get_cmc() on both faces - flip cards will have one mana cost, split and adventure cards will have 2
    most data will be specific to the card, Oracle Text is specific to card faces object"""
    
    card1 = the_card['card_faces'][0]
    card2 = the_card['card_faces'][1]
    face1_layout = the_card['layout']
    face1_colours = str(the_card['colors'])
    face1_colourID = str(the_card['color_identity'])
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
        if not face1_keywords : face1_keywords.append (' ')
    except:
        face1_keywords = "[]"
        print ("Exception encountered searching for 'keywords' - Split_Card_JSON")
        
    """Handling Creature and Planeswalker stats, if applicable """
    if "creature" in face1_type.lower():
        try:
            face1_power = card1['power']
            face1_toughness = card1['toughness']
        except:
            print ("Encountered exception attempting to access " , face1_name, "'s power/toughness - Split_Card_JSON (face 1)")
            face1_power = "-"
            face1_toughness = "-"    
    else:
        face1_power = "-"
        face1_toughness = "-"

    if "creature" in face2_type.lower():    
        try:
            face2_power = card2['power']
            face2_toughness = card2['toughness']
        except:
            print ("Encountered exception attempting to access " , face2_name, "'s power/toughness - Split_Card_JSON (face 2)")
            face2_power = "-"
            face2_toughness = "-"
    else:        
        face2_power = "-"
        face2_toughness = "-"

    face1_loyalty = "-"
    face2_loyalty = "-"
    ## This next section is only needed if a Planeswalker ends up on a split card, I'd kinda like to see that..
    # if 'planeswalker' in face1_type.lower():    
    #     try:
    #         face1_loyalty = the_card['loyalty']
    #     except:
    #         print ("encountered exception accessing ", face1_name, face1_type.lower(), "  (face1)  loyalty - Split_Card_JSON")
    #         face1_loyalty = "-"
    # else: face1_loyalty = "-"
    # 
    # if 'planeswalker' in face2_type.lower():    
    #     try:
    #         face2_loyalty = the_card['loyalty']
    #     except:
    #         face2_loyalty = "-"
    # else:
    #     print ("encountered exception accessing ", face2_name, face2_type.lower(), " (face2) loyalty - Split_Card_JSON")
    #     face2_loyalty = "-"
    
    

    """Adding to SQL tables: 'GrandtableSplit' and/or 'GrandtableSplit_Condensed'"""        
    mtg_sql.insert_splitcard_from_JSON(face1_name, face2_name, face1_layout, face1_colours, face1_colourID, face1_manacost, face1_cmc, face1_type, face1_text,
                          face1_keywords, face1_power, face1_toughness, face1_loyalty, face1_rarity, face1_images)
    mtg_sql.insert_splitcard_from_JSON(face2_name, face1_name, face1_layout, face1_colours, face1_colourID, face2_manacost, face2_cmc, face2_type, face2_text,
                          face1_keywords, face2_power, face2_toughness, face2_loyalty, face1_rarity, face1_images)

    add_this = face1_name+ " // "+ face2_name
    mtg_sql.insert_cardref(add_this, "Face_Cards_Condensed")
        
def Double_Faced_Card_JSON(the_card):
    """ Used for processing JSON data for cards of the following layouts:
    'transform' , 'modal_dfc' ,  'double_faced_token' , 'double_sided'
    Parameter:  the_card : Card object in JSON format from https://scryfall.com/docs/api/bulk-data
    Returns: nothing  , RUNS insert_splitcard_from_JSON() to add to 'GrandtableSplit' and 'GrandtableSplit_Condensed' tables (like Split_Card)
    Fetches  names, colors, color_identity, mana_costs, cmcs, card types, oracle texts, keywords, powers, toughness', loyalty's,
    raritys, image uris (urls?)
    RUNS regex_get_cmc() on both faces  - transform cards will only have 1 mana cost
    most data will be specific to the card, Oracle Text is specific to card faces object """
    
    face1_layout = the_card['layout']  # there is only one layout for the card, but named in face1_layout
    face1_colourID = str(the_card['color_identity'])
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
        if not face1_keywords : face1_keywords.append (' ')
    except:
        face1_keywords = "[]"
        print ("Exception encountered searching for 'keywords' - Double_Faced_Card_JSON")        
    if "creature" in face1_type.lower():
        try:
            face1_power = card1['power']
            face1_toughness = card1['toughness']
        except:
            print ("Encountered exception attempting to access ", face1_name, " power/toughness (side 1) - Double_Faced_Card_JSON")    
            face1_power = "-"
            face1_toughness = "-"
    else:
        face1_power = "-"
        face1_toughness = "-"
        
    if "creature" in face2_type.lower():
        try:            
            face2_power = card2['power']
            face2_toughness = card2['toughness']
        except:
            face2_power = "-"
            face2_toughness = "-"
            print ("Encountered exception attempting to access ", face2_name, " power/toughness  (side 2) - Double_Faced_Card_JSON")
    else:
        face2_power = "-"
        face2_toughness = "-"
        
    if 'planeswalker' in face1_type.lower():
        try:
            face1_loyalty = card1['loyalty']
        except:
            face1_loyalty = "-"
            print ("Encountered exception attempting to access ", face1_name, "'s loyalty - Double_Faced_Card_JSON")
    else: face1_loyalty = "-"
            
    if 'planeswalker' in face2_type.lower():
        if 'planeswalker' in face1_type.lower():
            ## Both sides of card are Planeswalkers and share the same Loyalty counters
            try:
                face2_loyalty = card1['loyalty']
            except:
                face2_loyalty = "-"
                print ("Encountered exception attempting to access ", face2_name, "'s loyalty - Double_Faced_Card_JSON")
        else:
            ## Only side 2 of the card is a Planeswalker, so card2['loyalty'] should be valid..?
            try:
                face2_loyalty = card2['loyalty']
            except:
                face2_loyalty = "-"
                print ("Encountered exception attempting to access ", face2_name, "'s loyalty - Double_Faced_Card_JSON")
                
    else: face2_loyalty = "-"

    ## Adding to SQL tables: 'GrandtableSplit' and/or 'GrandtableSplit_Condensed'
    mtg_sql.insert_splitcard_from_JSON(face1_name, face2_name, face1_layout, face1_colours, face1_colourID, face1_manacost, face1_cmc, face1_type, face1_text,
                          face1_keywords, face1_power, face1_toughness, face1_loyalty, face1_rarity, face1_images)
    
    mtg_sql.insert_splitcard_from_JSON(face2_name, face1_name, face1_layout, face1_colours, face1_colourID, face2_manacost, face2_cmc, face2_type, face2_text,
                          face1_keywords, face2_power, face2_toughness, face2_loyalty, face1_rarity, face1_images)

    add_this = face1_name+ " // "+ face2_name
    # Add the full card name to the Cardref table
    mtg_sql.insert_cardref(add_this, "Face_Cards_Condensed")    
    
def Ignore_Card_JSON(the_card):
    """planar, art series, scheme and the other obscure card types are just ignored"""
    # ignored_counter = ignored_counter + 1
    # print ("Skipped card :",the_card['name'], " : ", the_card['layout'])
    pass

convert_layout_JSON = {
    'normal' : Single_Sided_Card_JSON,
    'meld' : Single_Sided_Card_JSON,
    'saga' : Single_Sided_Card_JSON,
    'class' : Single_Sided_Card_JSON,
    'leveler' : Single_Sided_Card_JSON,
    'host' : Single_Sided_Card_JSON,
    'augment' : Single_Sided_Card_JSON,
    'emblem' : Single_Sided_Card_JSON,
    'split' : Split_Card_JSON,
    'flip' : Split_Card_JSON,
    'adventure' : Split_Card_JSON,
    'transform' : Double_Faced_Card_JSON,
    'modal_dfc' : Double_Faced_Card_JSON,
    'double_sided' : Double_Faced_Card_JSON,
    'token' : Ignore_Card_JSON,
    'double_faced_token' : Ignore_Card_JSON,
    'planar' : Ignore_Card_JSON,
    'art_series' : Ignore_Card_JSON,
    'scheme' : Ignore_Card_JSON,
    'vanguard' : Ignore_Card_JSON
}
def select_case_layout_JSON(layout, the_card):
    """The layout will determine which table the card gets added to
    called by main()"""
    execute_function = convert_layout_JSON.get(layout, "Invalid type")
    return execute_function(the_card)

def main():
    """ Adds all items from the specified JSON file into the Grandtable, GrandtableCondensed, GrandtableSplit, and GrandtableSplitCondensed
    Timed process: August 18: 6min 28sec   """
    begin_time = time.time()
    print (time.localtime(begin_time))
    Current_Folder = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
    Root_Folder = Path(Current_Folder).parent
    data_folder = Root_Folder / "db"
    latest_card_json = data_folder / "all-cards-20210818091127.json"
    counter = 0
    # latest_card_json = data_folder / 'all-cards-20210818091127.json'  # Current full database, check https://scryfall.com/docs/api/bulk-data for
                                                                        ### latest version
    # latest_card_json = data_folder / 'MTG some cards testfile.json'  # Much smaller file with < 900 records
    mtg_sql.cur.execute("DROP TABLE IF EXISTS 'CardRef'")
    mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Grandtable'")
    mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableCondensed'")
    mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableSplit'")
    mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableSplitCondensed'")
    mtg_sql.check_all_tables()
    with open(latest_card_json, encoding='utf-8') as f:
        data = json.load(f)
    for card in data:#['name']:
        if card['lang'] == "en":
            try:        
                counter += 1
                select_case_layout_JSON(card['layout'], card)
            except Exception as e:
                counter -= 1
                print ("Encountered exception accessing ",card['name'] , " - main import")
    print (counter, " records found")
    end_time = time.time()
    run_time = end_time - begin_time
    print (time.localtime(end_time))
    print ("Runtime :", round(run_time,3), " seconds")    
    # latest_card_json.close()
if __name__ == '__main__': main()