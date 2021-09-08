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

# import json   - if I start using the downloaded complete json file, however as new sets come out, i might want to stick with web queries
import time
import sqlite3
import csv
import sys
import scrython
import os
from pathlib import Path
# from mtg_classes import *
import mtg_regex
# from mtg_regex import *
# from mtg_mtg_sql.insert_ import regex_searchmode
# from json_load import *

Current_Folder = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
Root_Folder = Path(Current_Folder).parent
data_folder = Root_Folder / "db"
file_to_open = data_folder / "MTG.db"

db = sqlite3.connect(file_to_open)
cur = db.cursor()

""" INSERT INTO TABLES ###   START ### """

def insert_card_from_JSON(name, colors, colorid, manacost, cmc, c_type, oracletext, keywords, power, toughness, loyalty, rarity, image):
    # sqlite_insert_with_param = """INSERT OR IGNORE INTO Grandtable (Name, Colors, Colour_ID, Mana_Cost, CMC, Card_Type,
    # Oracle_Text, Keywords, Power, Toughness, Loyalty, Rarity, Image_URIs) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    
    sqlite_insert_with_param = """INSERT OR IGNORE INTO GrandtableCondensed (Name, Colors, Colour_ID, Mana_Cost, CMC, Card_Type,
    Oracle_Text, Keywords, Power, Toughness, Loyalty, Rarity, Image_URIs) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    
    add_tuple_to_sql = (name, colors, colorid, manacost, cmc, c_type, oracletext, keywords, power, toughness, loyalty, rarity, image)

    # print (sqlite_insert_with_param, add_tuple_to_sql)
    with db:
        cur.execute(sqlite_insert_with_param, add_tuple_to_sql)

def insert_splitcard_from_JSON(name1, name2, layout, colors, colorid, manacost, cmc, c_type, oracletext, keywords, power, toughness, loyalty, rarity, image):
    # sqlite_insert_with_param1 = """INSERT OR IGNORE INTO GrandtableSplit (Face_Name, Flip_Name, Layout, Colors, Colour_ID, Mana_Cost, CMC,
    # Type_Line, Oracle_Text, Keywords, Power, Toughness, Loyalty, Rarity, Image_URIs) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    
    sqlite_insert_with_param = """INSERT OR IGNORE INTO GrandtableSplitCondensed (Face_Name, Flip_Name, Layout, Colors, Colour_ID, Mana_Cost, CMC,
    Type_Line, Oracle_Text, Keywords, Power, Toughness, Loyalty, Rarity, Image_URIs) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    add_tuple_to_sql = (name1, name2, layout, colors, colorid, manacost, cmc, c_type, oracletext, keywords, power, toughness, loyalty, rarity, image)
    # print (sqlite_insert_with_param, add_tuple_to_sql)
    with db:
        # cur.execute(sqlite_insert_with_param1, add_tuple_to_sql)
        cur.execute(sqlite_insert_with_param, add_tuple_to_sql)

def insert_card(name, clr_ID, mana_cost, cmc, c_type, keywords, is_legend, has_etb, has_ramp, has_draw, has_target, has_wipe, has_activated, has_triggered, image_url, oracle_text):
    sqlite_insert_with_param = """INSERT OR IGNORE INTO Cards_Condensed (Name, Colour_ID, Mana_Cost, CMC, Card_Type, Keywords, Legendary, ETB, Ramp, Draw, Target, Broad, Activated, Triggered, Image_URL, Oracle_Text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    
    # sqlite_insert_with_param1 = """INSERT OR IGNORE INTO Cards (Name, Colour_ID, Mana_Cost, CMC, Card_Type, Keywords, Legendary, ETB, Ramp, Draw, Target, Broad, Activated, Triggered, Image_URL, Oracle_Text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""" 
    add_tuple_to_sql = (name, str(clr_ID), str(mana_cost), int(cmc), c_type, str(keywords), str(is_legend), str(has_etb), str(has_ramp), str(has_draw), str(has_target), str(has_wipe), str(has_activated), str(has_triggered), image_url, oracle_text)

    with db:
        # cur.execute(sqlite_insert_with_param1, add_tuple_to_sql)
        cur.execute(sqlite_insert_with_param, add_tuple_to_sql)

def insert_face_card(name, layout, flipname, clr_ID, mana_cost, cmc, c_type, keywords, is_legend, has_etb, has_ramp, has_draw, has_target, has_wipe, has_activated, has_triggered, image_url, oracle_text):
# name, layout, flipname, clr_ID, cost, c_type, is_legendary, keywords, has_ETB, has_ramp, has_draw, has_target, has_wipe, has_activated, has_triggered, image_url, oracle_text
    sqlite_insert_with_param = """INSERT OR IGNORE INTO Face_Cards_Condensed (Name, Layout, Flip_Name, Colour_ID, Mana_Cost, CMC, Card_Type, Keywords, Legendary,
    ETB, Ramp, Draw, Target, Broad, Activated, Triggered, Image_url, Oracle_Text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    
    # sqlite_insert_with_param1 = """INSERT OR IGNORE INTO Face_Cards (Name, Layout, Flip_Name, Colour_ID, Mana_Cost, CMC, Card_Type, Keywords, Legendary,
    # ETB, Ramp, Draw, Target, Broad, Activated, Triggered, Image_url, Oracle_Text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    add_tuple_to_sql = (name, layout, flipname, str(clr_ID), str(mana_cost), int(cmc), c_type, str(keywords), is_legend, str(has_etb), str(has_ramp), str(has_draw), str(has_target), str(has_wipe), str(has_activated), str(has_triggered), image_url, oracle_text)

    # print (sqlite_insert_with_param, add_tuple_to_sql)
    with db:
        # cur.execute(sqlite_insert_with_param1, add_tuple_to_sql)
        cur.execute(sqlite_insert_with_param, add_tuple_to_sql)

def insert_guild(code, name):
    sql_insert_with_param = """INSERT OR IGNORE INTO Clr_ID (id_Code, Guild_Name) VALUES (?, ?)"""
    listcode = list(code)
    add_tuple_to_sql = (str(listcode), name)
    with db:
        # cur.execute("INSERT OR IGNORE INTO Clr_ID VALUES (:id, :guild)", {'id': code,'guild': name})
        cur.execute(sql_insert_with_param, add_tuple_to_sql)

def insert_land(name, clr_ID, mana, mana_clr, act_abil):
    sqlite_insert_with_param = "INSERT OR IGNORE INTO Lands (Name, Colour_ID, Max_Mana, Mana_Clrs, Activated_Abilities) VALUES (?, ?, ?, ?, ?)"
    add_tuple_to_sql = (name, str(clr_ID), mana, str(mana_clr), act_abil)
    with db:
        cur.execute(sqlite_insert_with_param, add_tuple_to_sql)
    
def insert_creature(name, cr_type, cmc, power, toughness, keywords):
    sqlite_insert_with_param = "INSERT OR IGNORE INTO Creatures (Name, Creature_Type, CMC, Power, Toughness, Keywords) VALUES (?, ?, ?, ?, ?, ?)"
    add_tuple_to_sql = (name, cr_type, cmc, power, toughness, keywords)
    with db:
        cur.execute(sqlite_insert_with_param, add_tuple_to_sql)
                
def insert_spell(name, s_type, healing, damage):
    sqlite_insert_with_param = "INSERT OR IGNORE INTO Spells (Name, Spell_Type, Healing, Damage) VALUES (?, ?, ?, ?)"
    add_tuple_to_sql = (name, s_type, healing, damage)
    with db:
        cur.execute(sqlite_insert_with_param, add_tuple_to_sql)

def insert_cardref(name, table):
    sqlite_insert_with_param = "INSERT OR IGNORE INTO Cardref (Card_Name, Table_Name) VALUES (?, ?)"
    add_tuple_to_sql = (str(name), str(table))
    with db:
        cur.execute(sqlite_insert_with_param, add_tuple_to_sql)    

def insert_planeswalker(name, loyalty, is_passive, boost_ability, cost_ability, ultimate):
    sqlite_insert_with_param = """INSERT OR IGNORE INTO Planeswalkers (Name, Loyalty, Is_Passive, Boost_Ability, Cost_Ability, Ultimate)
            VALUES (?, ?, ?, ?, ?, ?)"""
    add_tuple_to_sql = (name, loyalty, is_passive, boost_ability, cost_ability, ultimate)
    with db:
        cur.execute(sqlite_insert_with_param, add_tuple_to_sql)

def insert_deck(d_id, name, clr_ID , commander, partner, tier, decklist, avg_cmc, lands, ramp, card_draw, target_removal, board_wipe, etb, status, location, notes):
    sqlite_insert_with_param = """INSERT OR IGNORE INTO All_Decks (id_Code, Deck_Name, Colour_ID, Commander, Partner, Deck_Tier, 
            Deck_list, Avg_CMC, Lands, Ramp, Draw, Target_Removal, Board_Wipe, ETB_Effects, Status, Location, Notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    add_tuple_to_sql = (d_id, name, str(clr_ID) , commander, partner, str(tier), decklist, avg_cmc, lands, ramp, card_draw, target_removal, board_wipe, etb, status, location, notes)
    with db:
        cur.execute(sqlite_insert_with_param, add_tuple_to_sql)

def insert_game(ID, playerlist, winner, loser, turns, notes):
    p1 = ""
    p2 = ""
    p3 = ""
    p4 = ""
    p5 = ""
    p6 = ""
    
    with db:
        # cur.execute("""INSERT INTO Test_Matches VALUES (
        #             :id, :p1, :p2, :p3, :p4, :p5, :p6, :winner, :loser, :turns, :notes)
        #             """, {'gm_ID': ID,'winner': winner, 'loser': loser, 'turns': turns, 'notes': notes, 'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4, 'p5': p5,'p6': p6})
        cur.execute("""INSERT INTO Test_Matches VALUES (
                    :gm_ID, :p1, :p2, :p3, :p4, :p5, :p6, :winner, :loser, :turns, :notes)
                    """, {'gm_ID': ID,'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4, 'p5': p5, 'p6': p6, 'winner': winner, 'loser': loser, 'turns': turns, 'notes': notes})

        count = 1
        maxcount = len(playerlist)
        for players in playerlist:
        
            sqlstatement = """UPDATE Test_Matches SET Deck_""" + str(count) + """ = """ + '"' + players + '"'+ """ WHERE gm_ID = """ + str(ID)            
                        
            print(sqlstatement)
            # cur.execute(sqlstatement)
            count += 1

def import_into_deck(deck_name, card_name, card_type, qty, sideboard):
    sqlite_insert_with_param = "INSERT OR IGNORE INTO "+deck_name+" (Name, Card_Type, Qty, Sideboard) VALUES (?, ?, ?, ?)"

    # add_tuple_to_sql = ('Attraxa?', 1, 'Yes', 'pile of shit')
    add_tuple_to_sql = (str(card_name), str(card_type), int(qty), str(sideboard))
    
    # print (sqlite_insert_with_param, add_tuple_to_sql)
    cur.execute(sqlite_insert_with_param, add_tuple_to_sql)
    
""" INSERT INTO TABLES ###   END ### """

def Remove_from_Table(table, name, table_field):  # based on exact matches, not partial
    sqlite_delete_statement = "DELETE from " + table + " WHERE " + table_field + "= :name"
    add_dict_to_sql = {'name': name}
    print("Executing SQL statement: " + sqlite_delete_statement,add_dict_to_sql)
     
    with db:
        cur.execute(sqlite_delete_statement,add_dict_to_sql)

""" VERIFY AND CREATION OF TABLES ###  START ###"""

def check_grandtable_condensed():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GrandtableCondensed' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'GrandtableCondensed' exists.")
        pass
    else:
        cur.execute("""
        CREATE TABLE GrandtableCondensed (
                        Name TEXT NOT NULL UNIQUE PRIMARY KEY,
                        Colors TEXT,
                        Colour_ID TEXT,                
                        Mana_Cost TEXT,
                        CMC INTEGER,
                        Card_Type TEXT,
                        Oracle_Text TEXT,
                        Keywords TEXT,
                        Power TEXT,
                        Toughness TEXT,
                        Loyalty TEXT,
                        Rarity TEXT,
                        Image_Uris TEXT)   """)
        print("New 'GrandtableCondensed' Table created.")
        
def check_grandtable_splitcondensed():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GrandtableSplitCondensed' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'GrandtableSplitCondensed' exists.")
        pass
    else:
        cur.execute("""
            CREATE TABLE GrandtableSplitCondensed (
                Face_Name TEXT NOT NULL PRIMARY KEY,
                Flip_Name TEXT NOT NULL,
                Layout TEXT,
                Colors TEXT,
                Colour_ID TEXT,
                Mana_Cost TEXT,
                CMC INTEGER,
                Type_Line TEXT,
                Oracle_Text TEXT,
                Keywords TEXT,
                Power TEXT,
                Toughness TEXT,
                Loyalty TEXT,
                Rarity TEXT,
                Image_Uris TEXT)    """)
        print("New 'GrandtableSplitCondensed' Table created.")
        
def check_grandtable():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Grandtable' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'Grandtable' exists.")
        pass
    else:
        cur.execute("""
            CREATE TABLE Grandtable (
                ROW_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Colors TEXT,
                Colour_ID TEXT,                
                Mana_Cost TEXT,
                CMC INTEGER,
                Card_Type TEXT,
                Oracle_Text TEXT,
                Keywords TEXT,
                Power TEXT,
                Toughness TEXT,
                Loyalty TEXT,
                Rarity TEXT,
                Image_Uris TEXT)    """)
        print("New 'Grandtable' Table created.")

def check_grandtable_split():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GrandtableSplit' ")
    if cur.fetchone()[0]==1 :
        pass
        # print("Table 'GrandtableSplit' exists.")
    else:
        cur.execute("""
            CREATE TABLE GrandtableSplit (
                ROW_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Face_Name TEXT NOT NULL,
                Flip_Name TEXT NOT NULL,
                Layout TEXT,
                Colors TEXT,
                Colour_ID TEXT,
                Mana_Cost TEXT,
                CMC INTEGER,
                Type_Line TEXT,
                Oracle_Text TEXT,
                Keywords TEXT,
                Power TEXT,
                Toughness TEXT,
                Loyalty TEXT,
                Rarity TEXT,
                Image_Uris TEXT)    """)
        print("New 'Grandtablesplit' Table created.")
        
def check_colour_id_table():
    
    cur.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Colour_Identity' """)
    if cur.fetchone()[0]==1 : 
        # print("Table 'Colour_Identity' exists.")
        pass
    else:
        cur.execute("CREATE TABLE Colour_Identity (id_Code TEXT, Guild_Name TEXT)")
#         recreate table and populate
        guilds = [MTG_Colours('R', 'MONO RED'),
              MTG_Colours('U', 'MONO BLUE'),
              MTG_Colours('W', 'MONO WHITE'),
              MTG_Colours('G', 'MONO GREEN'),
              MTG_Colours('B', 'MONO BLACK'),
              MTG_Colours('C', 'COLOURLESS'),
              MTG_Colours('BR', 'RAKDOS'),
              MTG_Colours('BG', 'GOLGARI'),
              MTG_Colours('BU', 'DIMIR'),
              MTG_Colours('BW', 'ORZHOV'),
              MTG_Colours('WU', 'AZORIUS'),
              MTG_Colours('WR', 'BOROS'),
              MTG_Colours('WG', 'SELESNYA'),
              MTG_Colours('UG', 'SIMIC'),
              MTG_Colours('RG', 'GRUUL'),
              MTG_Colours('UR', 'IZZET'),
              MTG_Colours('WUB', 'ESPER'),
              MTG_Colours('WUR', 'JESKAI'),
              MTG_Colours('WUG', 'BANT'),
              MTG_Colours('URB', 'GRIXIS'),
              MTG_Colours('URG', 'SULTAI'),
              MTG_Colours('BRG', 'JUND'),
              MTG_Colours('WRG', 'NAYA'),
              MTG_Colours('UGR', 'TEMUR'),
              MTG_Colours('WRB', 'MARDU'),
              MTG_Colours('WBG', 'ABZAN'),
              MTG_Colours('WURG', 'INK TREADER'),
              MTG_Colours('WUBR', 'YORE TILLER'),
              MTG_Colours('URBG', 'GLINT EYE'),
              MTG_Colours('WRBG', 'DUNE BROOD'),
              MTG_Colours('WUBG', 'WITCH MAW'),
              MTG_Colours('WUBRG', 'WOO BERG')              
              ]
        for records in guilds:
            insert_guild(records.id, records.guild)
            # print (records.id, records.guild)
            # "Instead of a cur.executemany statement"
        print("New 'Colour_Identity' Table created.")        

def check_clr_ID_table():
    cur.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Clr_ID' """)
    if cur.fetchone()[0]==1 : 
        # print("Table 'Clr_ID' exists.")
        pass
    else:
        cur.execute("CREATE TABLE Clr_ID (id_Code TEXT, Guild_Name TEXT)")
#         recreate table and populate
        guilds = [MTG_Colours('R', 'MONO RED'),
              MTG_Colours('U', 'MONO BLUE'),
              MTG_Colours('W', 'MONO WHITE'),
              MTG_Colours('G', 'MONO GREEN'),
              MTG_Colours('B', 'MONO BLACK'),
              MTG_Colours('C', 'COLOURLESS'),
              MTG_Colours('BR', 'RAKDOS'),
              MTG_Colours('BG', 'GOLGARI'),
              MTG_Colours('BU', 'DIMIR'),
              MTG_Colours('BW', 'ORZHOV'),
              MTG_Colours('WU', 'AZORIUS'),
              MTG_Colours('WR', 'BOROS'),
              MTG_Colours('WG', 'SELESNYA'),
              MTG_Colours('UG', 'SIMIC'),
              MTG_Colours('RG', 'GRUUL'),
              MTG_Colours('UR', 'IZZET'),
              MTG_Colours('WUB', 'ESPER'),
              MTG_Colours('WUR', 'JESKAI'),
              MTG_Colours('WUG', 'BANT'),
              MTG_Colours('URB', 'GRIXIS'),
              MTG_Colours('URG', 'SULTAI'),
              MTG_Colours('BRG', 'JUND'),
              MTG_Colours('WRG', 'NAYA'),
              MTG_Colours('UGR', 'TEMUR'),
              MTG_Colours('WRB', 'MARDU'),
              MTG_Colours('WBG', 'ABZAN'),
              MTG_Colours('WURG', 'INK TREADER'),
              MTG_Colours('WUBR', 'YORE TILLER'),
              MTG_Colours('URBG', 'GLINT EYE'),
              MTG_Colours('WRBG', 'DUNE BROOD'),
              MTG_Colours('WUBG', 'WITCH MAW'),
              MTG_Colours('WUBRG', 'WOO BERG')                            
              ]
        for records in guilds:
            insert_guild(records.id, records.guild)
            # print (records.id, records.guild)
            # "Instead of a cur.executemany statement"
        print("New 'Clr_ID' Table created.")    

def check_decks_table():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='All_Decks' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'All_Decks' exists.")
        pass
    else:
        cur.execute("""
            CREATE TABLE All_Decks (
                id_Code TEXT NOT NULL UNIQUE PRIMARY KEY,
                Deck_Name TEXT,
                Colour_ID TEXT,
                Commander TEXT,
                Partner TEXT,
                Deck_Tier TEXT,
                Deck_list TEXT,
                Avg_CMC REAL,
                Lands INTEGER,
                Ramp INTEGER,
                Draw INTEGER,
                Target_Removal INTEGER,
                Board_Wipe INTEGER,
                ETB_Effects INTEGER,
                Status TEXT,
                Location TEXT,
                Notes TEXT
            )
            """)
        print("New 'All_Decks' Table created.")

def check_cards_table():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Cards' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'Cards' exists.")
        pass
    else:
        cur.execute("""
            CREATE TABLE Cards (
                Row_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Colour_ID TEXT,
                Mana_Cost TEXT,
                CMC INTEGER,
                Card_Type TEXT,
                Keywords TEXT,
                Legendary TEXT,
                ETB TEXT,
                Ramp TEXT,
                Draw TEXT,
                Target TEXT,
                Broad TEXT,
                Activated TEXT,
                Triggered TEXT,
                Image_URL TEXT,
                Oracle_Text TEXT)    """)
        print("New 'Cards' Table created.")

def check_face_cards_table():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Face_Cards' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'Face_Cards' exists.")
        pass
    else:
        cur.execute("""
            CREATE TABLE Face_Cards (
                Row_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Layout TEXT,
                Flip_Name TEXT NOT NULL,
                Colour_ID TEXT,
                Mana_Cost TEXT,
                CMC INTEGER,
                Card_Type TEXT,
                Keywords TEXT,
                Legendary TEXT,
                ETB TEXT,
                Ramp TEXT,
                Draw TEXT,
                Target TEXT,
                Broad TEXT,
                Activated TEXT,
                Triggered TEXT,
                Image_URL TEXT,
                Oracle_Text TEXT)    """)
        print("New 'Face_Cards' Table created.")

def check_cards_condensed_table():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Cards_Condensed' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'Cards_Condensed' exists.")
        pass
    else:
        cur.execute("""
            CREATE TABLE Cards_Condensed (
                Name TEXT NOT NULL PRIMARY KEY,
                Colour_ID TEXT,
                Mana_Cost TEXT,
                CMC INTEGER,
                Card_Type TEXT,
                Keywords TEXT,
                Legendary TEXT,
                ETB TEXT,
                Ramp TEXT,
                Draw TEXT,
                Target TEXT,
                Broad TEXT,
                Activated TEXT,
                Triggered TEXT,
                Image_URL TEXT,
                Oracle_Text TEXT)    """)
        print("New 'Cards_Condensed' Table created.")

def check_face_cards_condensed_table():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Face_Cards_Condensed' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'Face_Cards_Condensed' exists.")
        pass
    else:
        cur.execute("""
            CREATE TABLE Face_Cards_Condensed (
                Name TEXT NOT NULL PRIMARY KEY,
                Layout TEXT,
                Flip_Name TEXT NOT NULL,
                Colour_ID TEXT,
                Mana_Cost TEXT,
                CMC INTEGER,
                Card_Type TEXT,
                Keywords TEXT,
                Legendary TEXT,
                ETB TEXT,
                Ramp TEXT,
                Draw TEXT,
                Target TEXT,
                Broad TEXT,
                Activated TEXT,
                Triggered TEXT,
                Image_URL TEXT,
                Oracle_Text TEXT)    """)
        print("New 'Face_Cards_Condensed' Table created.")
        
def check_test_matches_table():
    cur.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Test_Matches' """)
    if cur.fetchone()[0]==1 : 
        # print("Table 'Test_Matches' exists.")
        pass
    else:
        cur.execute("""CREATE TABLE Test_Matches (
                "gm_ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "Deck_1"    TEXT NOT NULL,
                "Deck_2"    TEXT NOT NULL,
                "Deck_3"    TEXT,
                "Deck_4"    TEXT,
                "Deck_5"    TEXT,
                "Deck_6"    TEXT,
                "Winner"    TEXT,
                "Loser"    TEXT,
                "Turn_number"    INTEGER,
                "Notes"    TEXT)""")
        print("New 'Test_Matches' Table created.")

def check_land_table():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Lands' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'Lands' exists.")
        pass
    else:
        cur.execute("""
            CREATE TABLE Lands (
                Name TEXT NOT NULL PRIMARY KEY,
                Colour_ID TEXT,
                Max_Mana INTEGER,
                Mana_Clrs TEXT,
                Activated_Abilities INTEGER
            )
            """)
        print("New 'Lands' Table created.")

def check_creatures_table():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Creatures' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'Creatures' exists.")
        pass
    else:
        cur.execute("""
            CREATE TABLE Creatures (
                Name TEXT NOT NULL PRIMARY KEY,
                Creature_Type TEXT,
                CMC INTEGER,
                Power INTEGER,
                Toughness INTEGER,
                Keywords TEXT)
            """)
        print("New 'Creatures' Table created.")

def check_spells_table():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Spells' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'Spells' exists.")
        pass
    else:
        cur.execute("""
            CREATE TABLE Spells (
                Name TEXT NOT NULL PRIMARY KEY,
                Spell_Type TEXT,
                Healing TEXT,
                Damage TEXT)
            """)
        print("New 'Spells' Table created.")
        
def check_planeswalker_table():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Planeswalkers' ")
    if cur.fetchone()[0]==1 : 
        # print("Table 'Planeswalkers' exists.")
        pass
    else:
        cur.execute("""
            CREATE TABLE Planeswalkers (
                Name TEXT NOT NULL PRIMARY KEY,
                Loyalty INTEGER,
                Is_Passive TEXT,
                Boost_Ability TEXT,
                Cost_Ability TEXT,
                Ultimate TEXT)
            """)
        print("New 'Planeswalkers' Table created.")

def check_cardref_table():
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Cardref' ")
    if cur.fetchone()[0]==1 : 
        print("Table 'Cardref' exists.")
    else:
        cur.execute("""
            CREATE TABLE Cardref (
                Card_Name TEXT NOT NULL PRIMARY KEY,
                Table_Name TEXT)
            """)
        print("New 'Cardref' Table created.")

def check_new_deck_table(deck_name):
    sql_statement = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='"+deck_name+"'"
    cur.execute(sql_statement)
    if cur.fetchone()[0]==1 : 
        print("Deck '",deck_name,"' exists.")
        # pass
    else:
        # sql_statement = 
        
        cur.execute("""
            CREATE TABLE """+deck_name+""" (
                Name TEXT PRIMARY KEY,
                Card_Type TEXT,
                Qty INTEGER,
                Sideboard TEXT,
                Card_notes TEXT)
            """)
        print("New '",deck_name,"' deck list created.")

def check_all_tables():  ## SEE IF ALL PRIMARY TABLES EXIST, AND CREATE IF REQUIRED, doesn't include deck tables ##
    check_colour_id_table()
    check_decks_table()
    check_cards_table()
    check_face_cards_table()
    check_cards_condensed_table()
    check_face_cards_condensed_table()
    check_test_matches_table()
    check_land_table()
    check_creatures_table()
    check_spells_table()
    check_planeswalker_table()
    check_grandtable()
    check_grandtable_split()
    check_grandtable_condensed()
    check_grandtable_splitcondensed()
    check_cardref_table()
            
"""### VERIFY AND CREATION OF TABLES ###  END  ###"""

"""### MANAGING DECK TABLES ###  START ###
    Steps for adding a deck
    1. Running import_deck_fromtxt() to import a deck list (exported from deckbox.org, etc) and give a name to that table, which will be referred to as deck_list 
    2. Running the calculate_deck(deck_list)  and get the deck's stats
    3. Running create_new_deck() to assemble the data and add it to All_Decks table      """

def check_cardref(card_name):  #check under which table a particular card needs to be looked up
    """    The Cardref table simply stores a list of the names of all printed cards and from which table their data need
    to be retrieved or else there will be missing cards on deck imports and the program won't know when to look in the
    double-sided card table since not all those cards have their names in the same format
    ie.  "Callo Jushi", not "Callo Jushi // Jaraku the Interloper"     """
    search_this = (card_name,)
    # print ()
    # print (card_name, " ", search_this)
    cur.execute("""SELECT Table_Name from Cardref WHERE Card_Name=?""",search_this)
    ref_table = cur.fetchone()
    # print (ref_table,type(ref_table))
    if ref_table is None:
        """Sometimes this search is done with double faced cards but only part of the card name was searched and it wasn't found exactly,
        so searching again will check for those"""
        card_name = card_name + " //%"
        this = "%"+card_name
        search_this = (this,)
        cur.execute("SELECT Table_Name from Cardref WHERE Card_Name LIKE ?",search_this)
        # print ("Trying with lighter requirements: SELECT Table_Name from Cardref WHERE Card_Name LIKE ?",search_this )
        ref_table = cur.fetchone()
        # if len(ref_table) > 0: print ("that's better ", ref_table)
    return ref_table

def handle_five_things(sql_cursor, qty, current_wp, current_dr, current_rmp, current_tg, current_etb, current_land, current_cmc):
    """it's called fivethings, even though it is up to 7, I think for face cards, it will even be 8.  Tomorrow, we'll see..
    Name of method may change or might not
    Called by calculate_deck() method, this will review the fetch data from the sql_cursor and increment the fields, and provide new updated counts
    """
    (new_wipe, new_draw, new_ramp, new_target, new_etb, new_land, new_cmc) = (current_wp, current_dr, current_rmp, current_tg, current_etb, current_land, current_cmc)
    
    if sql_cursor is None:
        pass ##placeholder..?
    else:  
        (cmc, wipe, draw, ramp, target, etb, card_type) = (sql_cursor[0], sql_cursor[1], sql_cursor[2],
                                                 sql_cursor[3], sql_cursor[4], sql_cursor[5], sql_cursor[6])
        if wipe != '-' :
            # print ("    :Found wipe card: ", wipe)
            new_wipe = current_wp + qty
        if draw != '-' :
            new_draw = current_dr + qty
            # print ("    :Found draw card: ", draw)            
        if 'land' not in card_type.lower():
            if ramp != '-' :
                # print ("    :Found ramp card: ", ramp)
                new_ramp = current_rmp + qty
        if target != '-' :
            # print ("    :Found target card: ", target)
            new_target = current_tg + qty
        if etb != '-' :
            # print ("    :Found etb card: ", etb)            
            new_etb = current_etb  + qty
        if 'land' in card_type.lower(): new_land = current_land + qty
        new_cmc = current_cmc + cmc * qty
        
    return (new_wipe, new_draw, new_ramp, new_target, new_etb, new_land, new_cmc)

def calculate_deck(deck_list):
    """Taking data from the deck_list and counting up all the ramp and     draw cards, etc
    returns: count of all board wipes, draw cards/engines, ramp cards, targeting cards, etb cards, lands, and average converted mana cost, or 'mana value')     """
    wipe_count = 0
    draw_count = 0
    ramp_count = 0
    target_count = 0
    etb_count = 0
    cmc_total = 0
    land_count = 0
    # avg_cmc = 0.0
    cur.execute("Select Name, Sideboard, Qty FROM "+deck_list)
    results = cur.fetchall()
    for card_name in results:
        double_faced_land_flag = False
        search_this = card_name 
        # print ("Any apostrophes here? ", search_this)
        name = search_this[0]
        score_multiplier = search_this[2]
        
        if search_this[1] == 'Yes':
            # print (search_this[0], search_this[1], " is sideboard")
            pass      # Sideboard placeholder...?
        else:
            """ check which table the data for the following card needs to come from"""
            this_table = check_cardref(search_this[0])
            
            if this_table is not None:
                if "Face_Cards_Condensed" in this_table:   
                    this_name = (name.split("//")[0].strip(),)
                    ## Convert 'Akki Lavarunner // Tok-Tok, Volcano Born' to just 'Akki Lavarunner' since the card data is represented as 2 rows
                    ## First search for 'Akki Lavarunner', and then search for 'Tok-Tok, Volcano Born' (which will be the next row)
                    cur.execute("""SELECT CMC, Broad, Draw, Ramp, Target, ETB, Card_Type, Flip_Name FROM Face_Cards_Condensed WHERE Name=?""",this_name)
                    fivethings = cur.fetchone()
                    (new_wipe, new_draw, new_ramp, new_target, new_etb, new_land, new_cmc) = handle_five_things(fivethings, score_multiplier, wipe_count, draw_count, ramp_count, target_count, etb_count, land_count, cmc_total)

                    if fivethings[6] is not None:
                        if 'land' in fivethings[6].lower() : double_faced_land_flag = True
                        
                    this_name = (fivethings[7],)
                    cur.execute("""SELECT CMC, Broad, Draw, Ramp, Target, ETB, Card_Type FROM Face_Cards_Condensed WHERE Name=?""",this_name)
                    ## Running this SELECT again so it counts the stats on both cards.. this will incidentally cause some strange average cmcs if
                    ## hypothetically a deck had several copies of a modal_dfc card 
                    fivethings = cur.fetchone()            
                    wipe_count, draw_count, ramp_count, target_count, etb_count, land_count, cmc_total  = handle_five_things(fivethings, score_multiplier, new_wipe, new_draw, new_ramp, new_target, new_etb, new_land, new_cmc)
                    # print (name, ": after this, current target count: " , target_count)                        
                    if fivethings[6] is not None:
                        if 'land' in fivethings[6].lower() and double_faced_land_flag == True : land_count -=1
                else:
                    ## Get card data for single sided card and if it has 
                    this_name = (name,)
                    cur.execute("""Select CMC, Broad, Draw, Ramp, Target, ETB, Card_Type FROM Cards_Condensed WHERE Name=?""",this_name)
                    fivethings = cur.fetchone()            
                    wipe_count, draw_count, ramp_count, target_count, etb_count, land_count, cmc_total = handle_five_things(fivethings, score_multiplier, wipe_count, draw_count, ramp_count, target_count, etb_count, land_count, cmc_total)
                    # print (name, ": after this, current etb count: " , target_count)            
    avg_cmc = round((cmc_total/ (100-land_count)),3)
    # print (cmc_total)
    # if len(partner) > 0 : print ("Partner: ", partner)
    print ("Average Mana Cost: ", avg_cmc)
    print ("ETB Count: ", etb_count)
    print ("target Count: ", target_count)
    print ("ramp Count: ", ramp_count)
    print ("draw Count: ", draw_count)
    print ("wipe Count: ", wipe_count)
    print ("Land Count: ", land_count)
    return (wipe_count, draw_count, ramp_count, target_count, etb_count, land_count, avg_cmc)
    
def import_deck_fromtxt(textfile, deck_list):
    """   CALLS import_into_deck()
    Parameters: 'textfile': pretty self explanatory
                'deck_list': Give a name for the SQLite table for the deck, starting with the letter 'z' for alphabetical ease """
    # deckpath = 'P:\Dev\SQL\Decks'
    
    Current_Folder = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
    Root_Folder = Path(Current_Folder).parent
    deck_folder = Root_Folder / "decks"
    load_deck = deck_folder / textfile
    
    sideboard_flag = False
    check_new_deck_table(deck_list)
    # print (textfile)    
    with open(load_deck, 'r') as f:
        lines = f.readlines()
        for line in lines:    
            if "Sideboard:" in line:
                # print ("hit sideboard flag")
                sideboard_flag = True
                cardqty = 0
                cardname = ""
            elif line == '\n':
                # print ("hit hard enter")
                cardqty = 0
                cardname = ""                
                # continue
            else:
                cardqty, cardname = line.split(" ",1)
            # print (cardname, " is getting ", cardqty, sideboard_flag, " sideboard")

            if '\n' in cardname: cardname = cardname.replace('\n',"")
            # print (cardname, type(check_cardref(cardname)))
            if type(check_cardref(cardname)) is tuple:
                this_table = (check_cardref(cardname)[0])
                # print ("SEARCHING TABLE: ",this_table)
            else:
                this_table = "Cards_Condensed"
            
            if this_table == "Face_Cards_Condensed":
                srch_name = (cardname.split("//")[0].strip(),)
            else:
                srch_name = (cardname,)

            # print ("SEARCHING CARD TYPE.. ", srch_name)
            cur.execute("SELECT Card_Type from "+this_table+" WHERE Name=?",srch_name)
            cardtype = cur.fetchone()

            # print (cardname, cardtype, type(cardtype))
            if type(cardtype) is tuple:
                ctype = (cardtype[0])
                # print ("CHANGING TO :", cardtype[0])
            else:
                ctype = cardtype
                
            if int(cardqty) > 0:
                #See what table the card data is and fetch the card type
                            
                if sideboard_flag == True:
                    sideboard = "Yes"
                else:
                    sideboard = "-"
                
                import_into_deck(deck_list, cardname, ctype, int(cardqty), sideboard)
        
    db.commit()

def create_new_deck(id_code, deck_name, commander, partner, tier, deck_list, status, location, notes):
    """Adding to the the All_Decks SQL table by running insert_deck().  RUNS calculate_deck(), then insert_deck()   Returns nothing.
        Parameters: deck_name: The official name of the deck 'Smithers, who is this gastropod?' (this is one of the few decks I named that doesn't name the commander)
                    commander: The official card name of the commander, nicknames don't count
                    partner: Partner commander if applicable, this will always always be blank or "-"
                    tier: Referring to primary- one each of the 32 different color combinations, or
                                        secondary- because you can't possibly limit oneself to only 1 Mardu deck!,
                                        or tertiary- because why not <Zoidberg>? maybe for playtests, or casual or playing against a niece or something
                    deck_list: The specific table name for the deck imported from the text file. Should start with a lowercase 'z' so they are at the bottom of the table list alphabetically
                    status: Active status of the deck {'ACTIVE', 'INACTIVE' (unassembled),'HARVESTED'(partially assembled)}
                    id_code:  Manually** created based on the commander's colour identity then follows the following fun little system (not alphabetical).
                            'a': aristocrat            'E': Evasion        'P': Populate            'H': Group Hug            
                            'A': Artifacts            'G': Graveyard        'S': Sacrifice            'Q': eQuipment
                            'b': blink                'I': Infect            'sc': spell copy        '$': buyback
                            'B': Battle                'K': Kicker            'T': Tribal                'g': gift
                            'c': creatures            'M': Madness        't': stealing            'xc': x-closer spells
                            'C': Counters            'm': morph            'U': Untap                'd': deathtouch
                            'cs': counterspells        'n': ninjitsu        'W': Word                '&': clone
                            'D': Draw                'N': eNchantments    'X': eXtra turns
                                                    'L': Land matters    'R': enRAGE!!
    """
    # print ("create_new_deck start..")
    # print ("Commander: ", commander)
    if len(partner) > 0: print ("Partner Commander: ", partner)
    
    (wipe_count, draw_count, ramp_count, target_count, etb_count, land_count, avg_cmc) = calculate_deck(deck_list)
    """Get the colour identity of the commander(s) """

    ## Check in which table the commander's colour ID can be found and retrieve it
    if type(check_cardref(commander)) is tuple: 
        this_table = (check_cardref(commander)[0])
    else:
        # this_table = "Cards_Condensed"
        this_table = check_cardref(commander)
    srch_commander = (commander,)
    cur.execute("SELECT Colour_ID from "+this_table+" WHERE Name=?",srch_commander)
    clr_ID = cur.fetchone()
    if type(clr_ID) is tuple:
        # print ("Converted clr_ID to ", clr_ID[0], " instead of ",clr_ID )
        clr_ID = clr_ID[0]

    ## Then if there is a Partner Commander, check in which table the partner's colour ID can be found and retrieve it
    if len(partner) > 0:
        if type(check_cardref(partner)) is tuple:
            this_table = (check_cardref(partner)[0])
            # print (this_table)
        else:
            # this_table = "Cards_Condensed"
            this_table = check_cardref(partner)
        srch_partner = (partner,)
        # print ("TABLE: ", this_table)
        cur.execute("SELECT Colour_ID from "+this_table+" WHERE Name=?",srch_partner)
        partner_colour =  cur.fetchone()
        if type(partner_colour) is tuple:
            # print ("Converted clr_ID to ", clr_ID[0], " instead of ",clr_ID )
            partner_colour = partner_colour[0]
            # print (partner_colour)
        clr_ID = clr_ID + partner_colour
                
    # print ("Deck colour ID: ", clr_ID)
    if not clr_ID: clr_ID = 'C..?'

    print ("insert_deck start..")
    insert_deck(id_code, deck_name, clr_ID , commander, partner, tier, deck_list, avg_cmc, land_count, ramp_count, draw_count, target_count, wipe_count, etb_count, status, location, notes)
    print ()

"""### TEMPORARY DECK TABLES   ###
  (preselected group of already downloaded txt files)"""
def import_all_decks(): 
    ##Maybe change this to a For loop later on with a directory reader, and auto-generate a table name..hmmm...    
    import_deck_fromtxt('RG-$U03_Alenalana Buyback X-closer.txt', 'zAlena_Halana')    
    import_deck_fromtxt("BR-01_Bottom's up Grenzo.txt", 'zBottoms_Up_Grenzo')
    import_deck_fromtxt('B-SG01_Shirei.txt', 'zShirei')
    import_deck_fromtxt('BG-CTok02_Hapatra.txt', 'zHapatra')
    import_deck_fromtxt('BRG-L01_Lord Windgrace Destructive Flow.txt', 'zWindgrace')
    import_deck_fromtxt('BRG-STok03 - I wanna be Korvold, sucka.txt', 'zKorvold')
    import_deck_fromtxt('C-A01_Traxos and his Hope of Gary Cooper.txt', 'zTraxos')
    import_deck_fromtxt('G unassembled - Toskiivasion.txt', 'zToski')
    import_deck_fromtxt("G-Id03_Fynn for fun cuz Marwyn's no nurturer.txt", 'zFynn')
    import_deck_fromtxt('R-AT04_Magda & (7 dwarves) Dorky, Broody, Horny, Loopy, Creepy, Twitchy, and Bill.txt', 'zMagda')
    import_deck_fromtxt("U-c&ok03_M'Orvar vor me.txt", 'zOrvar')
    import_deck_fromtxt("UB-n01_Yuriko's Ninjitsu.txt", 'zYuriko')
    import_deck_fromtxt('UBG-i02_Volrath the Infectious.txt', 'zVolrath')
    import_deck_fromtxt('UBR-T01_Inalla wizards ya had to include.txt', 'zInalla')
    import_deck_fromtxt("UG-KC03_Verazol's Kick'n it.txt", 'zVerazol')
    import_deck_fromtxt("UR-D01_It is a Niv Mizet visit, isn't it  it is.txt", 'zNivMizzet')
    import_deck_fromtxt('URBG-TG01_Kraum_Ikra Zombie uprising.txt', 'zKraumIkra')
    import_deck_fromtxt('URG-tS01_Yasova Stickyclaws.txt', 'zYasova')
    import_deck_fromtxt('W-TW02_Odric Keyword Smithy.txt', 'zOdric')
    import_deck_fromtxt('WB-a02_Teysa.txt', 'zTeysa')
    import_deck_fromtxt('WBG-Gcy02_Nethroi, Way-big Juicy Cycling.txt', 'zNethroi')
    import_deck_fromtxt('WBR-G02 - Ashley, the disgraceful Graverobber.txt', 'zAshley')
    import_deck_fromtxt("WBR-T01_Edgar Markov 'Hold the garlic'.txt", 'zEdgar_Markov')
    import_deck_fromtxt('WBRG-BE01_Saskia Combat Gimmicks.txt', 'zSaskia')
    import_deck_fromtxt('WB_unassembled - Tribal Lannister.txt', 'zLannister')
    import_deck_fromtxt('WG-Pok01_Trostani Tokens.txt', 'zTrostani')
    import_deck_fromtxt("WR unassembled - Koll's affordable dwarvish crap.txt", 'zKoll')
    import_deck_fromtxt('WR-01_Feat her to defeat her.txt', 'zFeather')
    import_deck_fromtxt("WRG-RG03_Obuun'dn't like me when I'm angry.txt", 'zObuun')
    import_deck_fromtxt('WU unassembled - No agony, no BRAGony.txt', 'zBrago')
    import_deck_fromtxt("WUB-N03_Leela's Enchanter.txt", 'zAlela')
    import_deck_fromtxt('WUB-Ut02_Freaky Merieke.txt', 'zMerieke')
    import_deck_fromtxt("WUBG-C01_Attraxa, Praetors' +1 Sword.txt", 'zAttraxa')
    import_deck_fromtxt('WU-EXbe01_Medomai - Timeless.txt', 'zMedomai')    
    import_deck_fromtxt('WUBR-A02_Silas & Akiri.txt', 'zSilasAkiri')
    import_deck_fromtxt('WUBRG-T01_Smithers, who is this gastropod.txt', 'zSmithers')
    import_deck_fromtxt('WUG-Lc02_I Chu-Chu-Chulane you.txt', 'zChulane')
    import_deck_fromtxt('WUR-T04_Kykar Spirit Splicer.txt', 'zKykar')
    import_deck_fromtxt("WURG-H01_Meletis says 'Hugs not thugs'.txt", 'zMeletis')

def create_all_decks():
    ## I ordered these by the boxes the decks are in
    create_new_deck('W-TW02', "Odric Keyword Smithy", 'Odric, Lunarch Marshal', "", "Primary", "zOdric", 'ACTIVE', 'SINGLE WHITE BOX', '')
    create_new_deck('U-c&ok03', "M'Orvar vor me", "Orvar, the All-Form", "", "Primary", "zOrvar", 'ACTIVE', 'SINGLE BLUE BOX', '')
    create_new_deck('B-SG01', "Shirei's Happy Sack", "Shirei, Shizo's Caretaker", "", "Primary", "zShirei", 'ACTIVE', 'SINGLE BLACK BOX', '')
    create_new_deck('R-AT04', "Magda & (7 dwarves) Dorky, Broody, Horny, Loopy, Creepy, Twitchy, and Bill", 'Magda, Brazen Outlaw', "", "Primary", "zMagda", 'ACTIVE', 'SINGLE RED BOX', '')    
    create_new_deck('G-Id03', "Fynn for fun cuz Marwyn's no nurturer", 'Fynn, the Fangbearer', "", "Primary", "zFynn", 'ACTIVE', 'SINGLE GREEN BOX', '')
    create_new_deck('UG-KC03', "Verazol's Kick'n it.txt", 'Verazol, the Split Current', "","Primary", "zVerazol", 'ACTIVE', 'SINGLE TURQUOISE', '')
    create_new_deck('URBG-TG01', "Zombie uprising!", "Kraum, Ludevic's Opus", "Ikra Shidiqi, the Usurper", "Primary", "zKraumIkra", 'ACTIVE', 'SINGLE BLUE BOX-unmarked', '')
    create_new_deck('WBG-Gcy02', "Way-big Juicy Cycling!", 'Nethroi, Apex of Death', "", "Primary", "zNethroi", 'ACTIVE', 'FANCY GREEN BOX', '')
    ## BORN OF THE GODS
    create_new_deck('BR-01', "Bottom's up, Grenzo!", 'Grenzo, Dungeon Warden', "", "Primary", "zBottoms_Up_Grenzo", 'ACTIVE', 'BORN OF THE GODS', '')
    create_new_deck('WUBG-C01', "Attraxa Praetors' +1 Sword", "Atraxa, Praetors' Voice", "", "Primary", "zAttraxa", 'ACTIVE', 'BORN OF THE GODS', '')
    create_new_deck('WBR-T01', 'Hold the garlic', 'Edgar Markov', "", "Primary", "zEdgar_Markov", 'ACTIVE', 'BORN OF THE GODS', '')
    ## DRAGONS MAZE
    create_new_deck('WUR-T04', 'Kykar Spirit Splicer',"Kykar, Wind's Fury", "", 'Primary','zKykar', 'ACTIVE', 'DRAGONS MAZE', '')
    create_new_deck('RG-$U03', "Alenalana Buyback X-Closer", 'Alena, Kessig Trapper', "Halana, Kessig Ranger", "Primary", "zAlena_Halana", 'ACTIVE', 'DRAGONS MAZE', '')    
    create_new_deck('UR-D01', "It is a Niv Mizet visit, isn't it?  it is!", 'Niv-Mizzet, Parun', "", "Primary", "zNivMizzet", 'ACTIVE', 'DRAGONS MAZE', '')
    ## PLAIN BLUE
    create_new_deck('WUB-Ut02', "Freaky Merieke!", 'Merieke Ri Berit', "", "Primary", "zMerieke", 'ACTIVE', 'PLAIN BLUE', '')
    create_new_deck('UB-n01', "Yuriko's Ninjitsu", "Yuriko, the Tiger's Shadow", "", "Primary", "zYuriko", 'ACTIVE', 'PLAIN BLUE', '')
    create_new_deck('UBR-T01', "Inalla wizards ya had to include", 'Inalla, Archmage Ritualist', "", "Primary", "zInalla", 'ACTIVE', 'PLAIN BLUE', '')
    ## PLAIN BLACK
    create_new_deck('WUBRG-T01', "Smithers, who is this gastropod?", 'Sliver Overlord', "", "Primary", "zSmithers", 'ACTIVE', 'PLAIN BLACK', '')
    create_new_deck('UBG-I02', "Volrath the Infectious", 'Volrath, the Shapestealer', "", "Primary", "zVolrath", 'ACTIVE', 'PLAIN BLACK', '')
    create_new_deck('C-A01', "Traxos and his Hope of Gary Cooper", 'Traxos, Scourge of Kroog', "", "Primary", "zTraxos", 'ACTIVE', 'PLAIN BLACK', '')
    ## THEROS
    create_new_deck('URG-tS01', "Yasova Stickyclaws", 'Yasova Dragonclaw', "", "Primary", "zYasova", 'ACTIVE', 'THEROS', '')
    create_new_deck('BRG-L01', "Lord Windgrace Destructive Flow", 'Lord Windgrace', "", "Primary", "zWindgrace", 'ACTIVE', 'THEROS', '')
    create_new_deck('WB-a02', "Teysa Aristrocrats", 'Teysa Karlov', "", "Primary", "zTeysa", 'ACTIVE', 'THEROS', '')
    ## HOUR OF DEVASTATION
    create_new_deck('WBRG-BE01', "Saskia Combat Gimmicks", 'Saskia the Unyielding', "", "Primary", "zSaskia", 'ACTIVE', 'HOUR OF DEVASTATION', '')
    create_new_deck('WRG-RG03', "Obuun'dn't like me when I'm angry!", 'Obuun, Mul Daya Ancestor', "", "Primary", "zObuun", 'ACTIVE', 'HOUR OF DEVASTATION', '')
    create_new_deck('BG-CTok02', "Hapatra", 'Hapatra, Vizier of Poisons', "", "Primary", "zHapatra", 'ACTIVE', 'HOUR OF DEVASTATION', '')
    ## IXALAN
    create_new_deck('WG-Pok01', "Trostani Tokens", "Trostani, Selesnya's Voice", "", "Primary", "zTrostani", 'ACTIVE', 'IXALAN', '')    
    create_new_deck('WU-EXbe01', "Medomai - Timeless", 'Medomai the Ageless', "", "Primary", "zMedomai", 'ACTIVE', 'IXALAN', '')    
    create_new_deck('WR-01', "Feat her to defeat her", 'Feather, the Redeemed', "", "Primary", "zFeather", 'ACTIVE', 'IXALAN', '')
    ## ORIGINS
    create_new_deck('WUBR-A02', "Batman & Robin", 'Silas Renn, Seeker Adept', "Akiri, Line-Slinger", "Primary", "zSilasAkiri", 'ACTIVE', 'ORIGINS', '')
    create_new_deck('WURG-H01', "Meletis says 'Hugs not thugs'","Kynaios and Tiro of Meletis", "", 'Primary','zMeletis', 'INACTIVE', 'ORIGINS', '')
    create_new_deck('WUG-Lc02', "I Chu-Chu-Chulane you", 'Chulane, Teller of Tales', "", 'Primary','zChulane', 'ACTIVE' , 'ORIGINS', '')

    ### SECONDARY DECKS ###
    create_new_deck('WBR-G02', "Ashley, the disgraceful Graverobber", 'Alesha, Who Smiles at Death', "", "Secondary", "zAshley", 'ACTIVE', 'RIVALS OF IXALAN', '')
    create_new_deck('WUB-N03', "Leela's Enchanter", 'Alela, Artful Provocateur', "", "Secondary", "zAlela", 'ACTIVE', 'RIVALS OF IXALAN', '')
    create_new_deck('BRG-STok03', "I wanna be Korvold, sucka!", 'Korvold, Fae-Cursed King', "", "Secondary", "zKorvold", 'ACTIVE', 'RIVALS OF IXALAN', '')

    ### ONLINE DECKS ###
    create_new_deck('WU-0X', "No agony, no BRAGOny", 'Brago, King Eternal', "", "Online", "zBrago", 'UNASSEMBLED', '-', '')        
    create_new_deck('WB-0X', "Tribal Lannister", 'General Kudro of Drannith', "", "Online", "zLannister", 'UNASSEMBLED', '-', '')    
    create_new_deck('WR-0X', "Koll's affordable dwarvish crap", 'Koll, the Forgemaster', "", "Online", "zKoll", 'UNASSEMBLED', '-', '')
    create_new_deck('G-0X', "Toskivasion", 'Toski, Bearer of Secrets', "", "Online", "zToski", 'UNASSEMBLED', '-', '')

def delete_all_zdecktables():
    cur.execute("DROP TABLE IF EXISTS 'zBottoms_Up_Grenzo'")
    cur.execute("DROP TABLE IF EXISTS 'zAlena_Halana'")
    cur.execute("DROP TABLE IF EXISTS 'zShirei' ")
    cur.execute("DROP TABLE IF EXISTS 'zHapatra'") 
    cur.execute("DROP TABLE IF EXISTS 'zWindgrace'") 
    cur.execute("DROP TABLE IF EXISTS 'zKorvold'") 
    cur.execute("DROP TABLE IF EXISTS 'zTraxos'") 
    cur.execute("DROP TABLE IF EXISTS 'zToski'")
    cur.execute("DROP TABLE IF EXISTS 'zFynn'") 
    cur.execute("DROP TABLE IF EXISTS 'zMagda'")
    cur.execute("DROP TABLE IF EXISTS 'zOrvar'") 
    cur.execute("DROP TABLE IF EXISTS 'zYuriko'") 
    cur.execute("DROP TABLE IF EXISTS 'zVolrath'") 
    cur.execute("DROP TABLE IF EXISTS 'zInalla'") 
    cur.execute("DROP TABLE IF EXISTS 'zVerazol'") 
    cur.execute("DROP TABLE IF EXISTS 'zNivMizzet'") 
    cur.execute("DROP TABLE IF EXISTS 'zKraumIkra'") 
    cur.execute("DROP TABLE IF EXISTS 'zYasova'") 
    cur.execute("DROP TABLE IF EXISTS 'zOdric'") 
    cur.execute("DROP TABLE IF EXISTS 'zTeysa'") 
    cur.execute("DROP TABLE IF EXISTS 'zNethroi'") 
    cur.execute("DROP TABLE IF EXISTS 'zAshley'") 
    cur.execute("DROP TABLE IF EXISTS 'zEdgar_Markov'") 
    cur.execute("DROP TABLE IF EXISTS 'zSaskia'") 
    cur.execute("DROP TABLE IF EXISTS 'zLannister'")
    cur.execute("DROP TABLE IF EXISTS 'zTrostani' ")    
    cur.execute("DROP TABLE IF EXISTS 'zKoll'")
    cur.execute("DROP TABLE IF EXISTS 'zFeather'") 
    cur.execute("DROP TABLE IF EXISTS 'zObuun' ")
    cur.execute("DROP TABLE IF EXISTS 'zBrago'")
    cur.execute("DROP TABLE IF EXISTS 'zAlela'") 
    cur.execute("DROP TABLE IF EXISTS 'zMerieke'") 
    cur.execute("DROP TABLE IF EXISTS 'zAttraxa'") 
    cur.execute("DROP TABLE IF EXISTS 'zMedomai'") 
    cur.execute("DROP TABLE IF EXISTS 'zSilasAkiri'") 
    cur.execute("DROP TABLE IF EXISTS 'zSmithers'") 
    cur.execute("DROP TABLE IF EXISTS 'zChulane'")
    cur.execute("DROP TABLE IF EXISTS 'zKykar'") 
    cur.execute("DROP TABLE IF EXISTS 'zMeletis'") 
    
"""### TEMPORARY DECK TABLES  ###  END  ###"""

"""### SAMPLE/TEST VERSION TEMPORARY DECK TABLES ###  START  ### """
def import_all_decks_sample(): 
    ##Maybe change this to a For loop later on with a directory reader, and auto-generate a table name..hmmm...    
    import_deck_fromtxt('RG-$U03_Alenalana Buyback X-closer.txt', 'zAlena_Halana')    
    import_deck_fromtxt("BR-01_Bottom's up Grenzo.txt", 'zBottoms_Up_Grenzo')
    import_deck_fromtxt('B-SG01_Shirei.txt', 'zShirei')
    import_deck_fromtxt('BG-CTok02_Hapatra.txt', 'zHapatra')
    import_deck_fromtxt('BRG-L01_Lord Windgrace Destructive Flow.txt', 'zWindgrace')
    import_deck_fromtxt('BRG-STok03 - I wanna be Korvold, sucka.txt', 'zKorvold')
    import_deck_fromtxt('C-A01_Traxos and his Hope of Gary Cooper.txt', 'zTraxos')
    import_deck_fromtxt('G unassembled - Toskiivasion.txt', 'zToski')
    import_deck_fromtxt("G-Id03_Fynn for fun cuz Marwyn's no nurturer.txt", 'zFynn')
    import_deck_fromtxt('R-AT04_Magda & (7 dwarves) Dorky, Broody, Horny, Loopy, Creepy, Twitchy, and Bill.txt', 'zMagda')
    import_deck_fromtxt("U-c&ok03_M'Orvar vor me.txt", 'zOrvar')
    import_deck_fromtxt("UB-n01_Yuriko's Ninjitsu.txt", 'zYuriko')
    import_deck_fromtxt('UBG-i02_Volrath the Infectious.txt', 'zVolrath')
    import_deck_fromtxt('UBR-T01_Inalla wizards ya had to include.txt', 'zInalla')
    import_deck_fromtxt("UG-KC03_Verazol's Kick'n it.txt", 'zVerazol')
    import_deck_fromtxt("UR-D01_It is a Niv Mizet visit, isn't it  it is.txt", 'zNivMizzet')
    import_deck_fromtxt('URBG-TG01_Kraum_Ikra Zombie uprising.txt', 'zKraumIkra')
    import_deck_fromtxt('URG-tS01_Yasova Stickyclaws.txt', 'zYasova')
    import_deck_fromtxt('W-TW02_Odric Keyword Smithy.txt', 'zOdric')
    import_deck_fromtxt('WB-a02_Teysa.txt', 'zTeysa')
    import_deck_fromtxt('WBG-Gcy02_Nethroi, Way-big Juicy Cycling.txt', 'zNethroi')
    import_deck_fromtxt('WBR-G02 - Ashley, the disgraceful Graverobber.txt', 'zAshley')
    import_deck_fromtxt("WBR-T01_Edgar Markov 'Hold the garlic'.txt", 'zEdgar_Markov')
    import_deck_fromtxt('WBRG-BE01_Saskia Combat Gimmicks.txt', 'zSaskia')
    import_deck_fromtxt('WB_unassembled - Tribal Lannister.txt', 'zLannister')
    import_deck_fromtxt('WG-Pok01_Trostani Tokens.txt', 'zTrostani')
    import_deck_fromtxt("WR unassembled - Koll's affordable dwarvish crap.txt", 'zKoll')
    import_deck_fromtxt('WR-01_Feat her to defeat her.txt', 'zFeather')
    import_deck_fromtxt("WRG-RG03_Obuun'dn't like me when I'm angry.txt", 'zObuun')
    import_deck_fromtxt('WU unassembled - No agony, no BRAGony.txt', 'zBrago')
    import_deck_fromtxt("WUB-N03_Leela's Enchanter.txt", 'zAlela')
    import_deck_fromtxt('WUB-Ut02_Freaky Merieke.txt', 'zMerieke')
    import_deck_fromtxt("WUBG-C01_Attraxa, Praetors' +1 Sword.txt", 'zAttraxa')
    import_deck_fromtxt('WU-EXbe01_Medomai - Timeless.txt', 'zMedomai')    
    import_deck_fromtxt('WUBR-A02_Silas & Akiri.txt', 'zSilasAkiri')
    import_deck_fromtxt('WUBRG-T01_Smithers, who is this gastropod.txt', 'zSmithers')
    import_deck_fromtxt('WUG-Lc02_I Chu-Chu-Chulane you.txt', 'zChulane')
    import_deck_fromtxt('WUR-T04_Kykar Spirit Splicer.txt', 'zKykar')
    import_deck_fromtxt("WURG-H01_Meletis says 'Hugs not thugs'.txt", 'zMeletis')

def create_all_decks_sample():
    ## I ordered these by the boxes the decks are in
    create_new_deck('W-TW02', "Odric Keyword Smithy", 'Odric, Lunarch Marshal', "", "Primary", "zOdric", 'ACTIVE', 'SINGLE WHITE BOX', '')
    create_new_deck('U-c&ok03', "M'Orvar vor me", "Orvar, the All-Form", "", "Primary", "zOrvar", 'ACTIVE', 'SINGLE BLUE BOX', '')
    create_new_deck('B-SG01', "Shirei's Happy Sack", "Shirei, Shizo's Caretaker", "", "Primary", "zShirei", 'ACTIVE', 'SINGLE BLACK BOX', '')
    create_new_deck('R-AT04', "Magda & (7 dwarves) Dorky, Broody, Horny, Loopy, Creepy, Twitchy, and Bill", 'Magda, Brazen Outlaw', "", "Primary", "zMagda", 'ACTIVE', 'SINGLE RED BOX', '')    
    create_new_deck('G-Id03', "Fynn for fun cuz Marwyn's no nurturer", 'Fynn, the Fangbearer', "", "Primary", "zFynn", 'ACTIVE', 'SINGLE GREEN BOX', '')
    create_new_deck('UG-KC03', "Verazol's Kick'n it.txt", 'Verazol, the Split Current', "","Primary", "zVerazol", 'ACTIVE', 'SINGLE TURQUOISE', '')
    create_new_deck('URBG-TG01', "Zombie uprising!", "Kraum, Ludevic's Opus", "Ikra Shidiqi, the Usurper", "Primary", "zKraumIkra", 'ACTIVE', 'SINGLE BLUE BOX-unmarked', '')
    create_new_deck('WBG-Gcy02', "Way-big Juicy Cycling!", 'Nethroi, Apex of Death', "", "Primary", "zNethroi", 'ACTIVE', 'FANCY GREEN BOX', '')
    ## BORN OF THE GODS
    create_new_deck('BR-01', "Bottom's up, Grenzo!", 'Grenzo, Dungeon Warden', "", "Primary", "zBottoms_Up_Grenzo", 'ACTIVE', 'BORN OF THE GODS', '')
    create_new_deck('WUBG-C01', "Attraxa Praetors' +1 Sword", "Atraxa, Praetors' Voice", "", "Primary", "zAttraxa", 'ACTIVE', 'BORN OF THE GODS', '')
    create_new_deck('WBR-T01', 'Hold the garlic', 'Edgar Markov', "", "Primary", "zEdgar_Markov", 'ACTIVE', 'BORN OF THE GODS', '')
    ## DRAGONS MAZE
    create_new_deck('WUR-T04', 'Kykar Spirit Splicer',"Kykar, Wind's Fury", "", 'Primary','zKykar', 'ACTIVE', 'DRAGONS MAZE', '')
    create_new_deck('RG-$U03', "Alenalana Buyback X-Closer", 'Alena, Kessig Trapper', "Halana, Kessig Ranger", "Primary", "zAlena_Halana", 'ACTIVE', 'DRAGONS MAZE', '')    
    create_new_deck('UR-D01', "It is a Niv Mizet visit, isn't it?  it is!", 'Niv-Mizzet, Parun', "", "Primary", "zNivMizzet", 'ACTIVE', 'DRAGONS MAZE', '')
    ## PLAIN BLUE
    create_new_deck('WUB-Ut02', "Freaky Merieke!", 'Merieke Ri Berit', "", "Primary", "zMerieke", 'ACTIVE', 'PLAIN BLUE', '')
    create_new_deck('UB-n01', "Yuriko's Ninjitsu", "Yuriko, the Tiger's Shadow", "", "Primary", "zYuriko", 'ACTIVE', 'PLAIN BLUE', '')
    create_new_deck('UBR-T01', "Inalla wizards ya had to include", 'Inalla, Archmage Ritualist', "", "Primary", "zInalla", 'ACTIVE', 'PLAIN BLUE', '')
    ## PLAIN BLACK
    create_new_deck('WUBRG-T01', "Smithers, who is this gastropod?", 'Sliver Overlord', "", "Primary", "zSmithers", 'ACTIVE', 'PLAIN BLACK', '')
    create_new_deck('UBG-I02', "Volrath the Infectious", 'Volrath, the Shapestealer', "", "Primary", "zVolrath", 'ACTIVE', 'PLAIN BLACK', '')
    create_new_deck('C-A01', "Traxos and his Hope of Gary Cooper", 'Traxos, Scourge of Kroog', "", "Primary", "zTraxos", 'ACTIVE', 'PLAIN BLACK', '')
    ## THEROS
    create_new_deck('URG-tS01', "Yasova Stickyclaws", 'Yasova Dragonclaw', "", "Primary", "zYasova", 'ACTIVE', 'THEROS', '')
    create_new_deck('BRG-L01', "Lord Windgrace Destructive Flow", 'Lord Windgrace', "", "Primary", "zWindgrace", 'ACTIVE', 'THEROS', '')
    create_new_deck('WB-a02', "Teysa Aristrocrats", 'Teysa Karlov', "", "Primary", "zTeysa", 'ACTIVE', 'THEROS', '')
    ## HOUR OF DEVASTATION
    create_new_deck('WBRG-BE01', "Saskia Combat Gimmicks", 'Saskia the Unyielding', "", "Primary", "zSaskia", 'ACTIVE', 'HOUR OF DEVASTATION', '')
    create_new_deck('WRG-RG03', "Obuun'dn't like me when I'm angry!", 'Obuun, Mul Daya Ancestor', "", "Primary", "zObuun", 'ACTIVE', 'HOUR OF DEVASTATION', '')
    create_new_deck('BG-CTok02', "Hapatra", 'Hapatra, Vizier of Poisons', "", "Primary", "zHapatra", 'ACTIVE', 'HOUR OF DEVASTATION', '')
    ## IXALAN
    create_new_deck('WG-Pok01', "Trostani Tokens", "Trostani, Selesnya's Voice", "", "Primary", "zTrostani", 'ACTIVE', 'IXALAN', '')    
    create_new_deck('WU-EXbe01', "Medomai - Timeless", 'Medomai the Ageless', "", "Primary", "zMedomai", 'ACTIVE', 'IXALAN', '')    
    create_new_deck('WR-01', "Feat her to defeat her", 'Feather, the Redeemed', "", "Primary", "zFeather", 'ACTIVE', 'IXALAN', '')
    ## ORIGINS
    create_new_deck('WUBR-A02', "Batman & Robin", 'Silas Renn, Seeker Adept', "Akiri, Line-Slinger", "Primary", "zSilasAkiri", 'ACTIVE', 'ORIGINS', '')
    create_new_deck('WURG-H01', "Meletis says 'Hugs not thugs'","Kynaios and Tiro of Meletis", "", 'Primary','zMeletis', 'INACTIVE', 'ORIGINS', '')
    create_new_deck('WUG-Lc02', "I Chu-Chu-Chulane you", 'Chulane, Teller of Tales', "", 'Primary','zChulane', 'ACTIVE' , 'ORIGINS', '')

    ### SECONDARY DECKS ###
    create_new_deck('WBR-G02', "Ashley, the disgraceful Graverobber", 'Alesha, Who Smiles at Death', "", "Secondary", "zAshley", 'ACTIVE', 'RIVALS OF IXALAN', '')
    create_new_deck('WUB-N03', "Leela's Enchanter", 'Alela, Artful Provocateur', "", "Secondary", "zAlela", 'ACTIVE', 'RIVALS OF IXALAN', '')
    create_new_deck('BRG-STok03', "I wanna be Korvold, sucka!", 'Korvold, Fae-Cursed King', "", "Secondary", "zKorvold", 'ACTIVE', 'RIVALS OF IXALAN', '')

    ### ONLINE DECKS ###
    create_new_deck('WU-0X', "No agony, no BRAGOny", 'Brago, King Eternal', "", "Online", "zBrago", 'UNASSEMBLED', '-', '')        
    create_new_deck('WB-0X', "Tribal Lannister", 'General Kudro of Drannith', "", "Online", "zLannister", 'UNASSEMBLED', '-', '')    
    create_new_deck('WR-0X', "Koll's affordable dwarvish crap", 'Koll, the Forgemaster', "", "Online", "zKoll", 'UNASSEMBLED', '-', '')
    create_new_deck('G-0X', "Toskivasion", 'Toski, Bearer of Secrets', "", "Online", "zToski", 'UNASSEMBLED', '-', '')

def delete_all_zdecktables_sample():
    cur.execute("DROP TABLE IF EXISTS 'zBottoms_Up_Grenzo'")
    cur.execute("DROP TABLE IF EXISTS 'zAlena_Halana'")
    cur.execute("DROP TABLE IF EXISTS 'zShirei' ")
    cur.execute("DROP TABLE IF EXISTS 'zHapatra'") 
    cur.execute("DROP TABLE IF EXISTS 'zWindgrace'") 
    cur.execute("DROP TABLE IF EXISTS 'zKorvold'") 
    cur.execute("DROP TABLE IF EXISTS 'zTraxos'") 
    cur.execute("DROP TABLE IF EXISTS 'zToski'")
    cur.execute("DROP TABLE IF EXISTS 'zFynn'") 
    cur.execute("DROP TABLE IF EXISTS 'zMagda'")
    cur.execute("DROP TABLE IF EXISTS 'zOrvar'") 
    cur.execute("DROP TABLE IF EXISTS 'zYuriko'") 
    cur.execute("DROP TABLE IF EXISTS 'zVolrath'") 
    cur.execute("DROP TABLE IF EXISTS 'zInalla'") 
    cur.execute("DROP TABLE IF EXISTS 'zVerazol'") 
    cur.execute("DROP TABLE IF EXISTS 'zNivMizzet'") 
    cur.execute("DROP TABLE IF EXISTS 'zKraumIkra'") 
    cur.execute("DROP TABLE IF EXISTS 'zYasova'") 
    cur.execute("DROP TABLE IF EXISTS 'zOdric'") 
    cur.execute("DROP TABLE IF EXISTS 'zTeysa'") 
    cur.execute("DROP TABLE IF EXISTS 'zNethroi'") 
    cur.execute("DROP TABLE IF EXISTS 'zAshley'") 
    cur.execute("DROP TABLE IF EXISTS 'zEdgar_Markov'") 
    cur.execute("DROP TABLE IF EXISTS 'zSaskia'") 
    cur.execute("DROP TABLE IF EXISTS 'zLannister'")
    cur.execute("DROP TABLE IF EXISTS 'zTrostani' ")    
    cur.execute("DROP TABLE IF EXISTS 'zKoll'")
    cur.execute("DROP TABLE IF EXISTS 'zFeather'") 
    cur.execute("DROP TABLE IF EXISTS 'zObuun' ")
    cur.execute("DROP TABLE IF EXISTS 'zBrago'")
    cur.execute("DROP TABLE IF EXISTS 'zAlela'") 
    cur.execute("DROP TABLE IF EXISTS 'zMerieke'") 
    cur.execute("DROP TABLE IF EXISTS 'zAttraxa'") 
    cur.execute("DROP TABLE IF EXISTS 'zMedomai'") 
    cur.execute("DROP TABLE IF EXISTS 'zSilasAkiri'") 
    cur.execute("DROP TABLE IF EXISTS 'zSmithers'") 
    cur.execute("DROP TABLE IF EXISTS 'zChulane'")
    cur.execute("DROP TABLE IF EXISTS 'zKykar'") 
    cur.execute("DROP TABLE IF EXISTS 'zMeletis'") 
    
"""### SAMPLE/TEST VERSION TEMPORARY DECK TABLES ###  END  ###"""

def main():
        ## CLEAR OLD TABLES IF NECESSARY  ##
    cur.execute("DROP TABLE IF EXISTS 'zDelete'")
    # check_all_tables()      ## SEE IF TABLES EXIST, AND CREATES IF REQUIRED ##

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'z%' ")
    result = cur.fetchall()
    print (result)

    print ("SQL SHIT")
    db.commit()
if __name__ == '__main__': main()