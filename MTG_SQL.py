#  2021  Paul Austin
# Thanks to https://scryfall.com/docs/api

import time
import sqlite3
import csv
import sys
import scrython
# import pypyodbc as odbc
from MTG_Classes import *

db = sqlite3.connect('MTG.db')
cur = db.cursor()

def insert_guild(code, name):
	with db:
		cur.execute("INSERT INTO Colour_Identity VALUES (:id, :guild)", {'id': code,'guild': name})

def find_guild(code):
	cur.execute("SELECT * FROM Colour_Identity WHERE id_Code=:id", {'id': code})	
	return cur.fetchall()

def get_colour_id(mana_cost):
	# convert_this = '{2W}{2U}{2B}{2R}{2G}'
	clr_id = ""
	if 'W' in mana_cost: clr_id = clr_id + 'W'
	if 'U' in mana_cost: clr_id = clr_id + 'U'
	if 'B' in mana_cost: clr_id = clr_id + 'B'
	if 'R' in mana_cost: clr_id = clr_id + 'R'
	if 'G' in mana_cost: clr_id = clr_id + 'G'
	if len(clr_id) < 1: clr_id = 'C'
	# print (mana_cost + " has the colour code: " + clr_id)
	return clr_id
	
def get_total_cmc(mana_cost):
	reduced_convert = mana_cost.replace('}', ' ')
	reduce_more = reduced_convert.replace('{', '')
	split_cost = reduce_more.split(' ')
	split_cost.pop()
	start_cost = 0
	for costs in split_cost:
		if costs.isalpha():
			try:
				start_cost = int(start_cost) + 1 #int(removed_g)
			except Exception:
				pass
		elif costs.isnumeric():
			try:
				start_cost = int(start_cost) + int(costs)
			except Exception:
				pass
		elif costs.isalnum():
			try:
				start_cost = int(start_cost) + 1
			except Exception:
				pass
	return start_cost
	
def insert_card(name, clr_ID, cmc, c_type, is_perm, is_legend, has_etb, has_ramp, has_draw, has_target, has_wipe, has_activated, has_triggered, is_passive):
	sqlite_insert_with_param = """INSERT OR IGNORE INTO Cards (Name, Colour_ID, Converted_Mana_Cost, Card_Type, Is_Permanent, IS_LEGENDARY,
	Has_ETB, Has_Ramp, Has_Draw, Has_Target, Has_Wipe, Has_Activated, Has_Triggered, Is_Passive) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
	
	add_tuple_to_sql = (name, clr_ID, cmc, c_type, is_perm, is_legend, has_etb, has_ramp, has_draw, has_target, has_wipe, has_activated, has_triggered, is_passive)

	with db:
		cur.execute(sqlite_insert_with_param, add_tuple_to_sql)

def insert_card_partial(name, type_line, mana_cost):
	"""Even without Scryfall queries, type_line and mana_cost will still be able to determine:
	colour ID ...  is_permanent .... legendary.   more than half the categories
	has ETB, Ramp, draw, target, wipe  will need to be determined by the card text	"""
	colour_id = get_colour_id(mana_cost)
	cmc = get_total_cmc(mana_cost)
	is_legendary = 'FALSE'
	is_permanent = 'TRUE'
	base_type = ''
	sub_type = ''
	if '-' in type_line:
		card_types = type_line.split('—')
		base_type = card_types[0]
		sub_type =  card_types[1]
	
	if 'LEGENDARY' in type_line.upper(): is_legendary = 'TRUE'
	
	if 'SORCERY' in type_line.upper():
		is_permanent = 'FALSE'
		base_type = 'Sorcery'
	
	if 'INSTANT' in type_line.upper():
		is_permanent = 'FALSE'
		base_type = 'Instant'

	if base_type == "" and sub_type == "":
		# print(name + '   ' + base_type + '   ' + sub_type  + '    ' + colour_id + '   ' + str(cmc) + '   ' + mana_cost )
		# print(type_line)
		base_type = type_line
	
	sqlite_insert_with_param = """INSERT OR IGNORE INTO Cards (Name, Colour_ID, Converted_Mana_Cost, Card_Type, Is_Permanent, IS_LEGENDARY)
			VALUES (?, ?, ?, ?, ?, ?)"""
	add_tuple_to_sql = (name, colour_id, cmc, base_type, is_permanent, is_legendary)
	# print(name + '   ' + base_type + '   ' + sub_type  + '    ' + colour_id + '   ' + str(cmc) + '   ' + mana_cost )
	cur.execute(sqlite_insert_with_param, add_tuple_to_sql)	

def insert_land(name, clr_ID, mana, has_additional):
	sqlite_insert_with_param = "INSERT OR IGNORE INTO Lands (Name, Colour_ID, Mana, Has_Additional) VALUES (?, ?, ?, ?)"
	add_tuple_to_sql = (name, clr_ID, mana, has_additional)
	with db:
		cur.execute(sqlite_insert_with_param, add_tuple_to_sql)
		
def insert_creature(name, cr_type, power, toughness):
	sqlite_insert_with_param = "INSERT OR IGNORE INTO Creatures (Name, Creature_Type, Power, Toughness) VALUES (?, ?, ?, ?)"
	add_tuple_to_sql = (name, cr_type, power, toughness)
	with db:
		cur.execute(sqlite_insert_with_param, add_tuple_to_sql)
		
def insert_spell(name, s_type, healing, damage):
	sqlite_insert_with_param = "INSERT OR IGNORE INTO Spells (Name, Spell_Type, Has_Healing, Has_Damage) VALUES (?, ?, ?, ?)"
	add_tuple_to_sql = (name, s_type, healing, damage)
	with db:
		cur.execute(sqlite_insert_with_param, add_tuple_to_sql)

def insert_art_ench(name, spell_type, activated_ability, triggered_ability, is_passive, description):
	sqlite_insert_with_param = """INSERT OR IGNORE INTO Artifacts_Enchantments (Name, Spell_Type, Activated_Ability, Triggered_Ability, Is_Passive, Description)
			VALUES (?, ?, ?, ?, ?, ?)"""
	add_tuple_to_sql = (name, spell_type, activated_ability, triggered_ability, is_passive, description)

	with db:
		cur.execute(sqlite_insert_with_param, add_tuple_to_sql)

def insert_planeswalker(name, loyalty, is_passive, boost_ability, cost_ability, ultimate):
	sqlite_insert_with_param = """INSERT OR IGNORE INTO Planeswalkers (Name, Loyalty, Is_Passive, Boost_Ability, Cost_Ability, Ultimate)
			VALUES (?, ?, ?, ?, ?, ?)"""
	add_tuple_to_sql = (name, loyalty, is_passive, boost_ability, cost_ability, ultimate)
	with db:
		cur.execute(sqlite_insert_with_param, add_tuple_to_sql)

def insert_deck(d_id, name, clr_ID , commander, num_clrs, tier, ramp, card_draw, target_removal, board_wipe):
	sqlite_insert_with_param = """INSERT OR IGNORE INTO All_Decks (id_Code, Deck_Name, Colour_ID, Commander,
			Number_Colours, Deck_Tier, Ramp, Draw, Target_Removal, Board_Wipe) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
	add_tuple_to_sql = (d_id, name, clr_ID , commander, num_clrs, tier, ramp, card_draw, target_removal, board_wipe)
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
		# 			:id, :p1, :p2, :p3, :p4, :p5, :p6, :winner, :loser, :turns, :notes)
		# 			""", {'gm_ID': ID,'winner': winner, 'loser': loser, 'turns': turns, 'notes': notes, 'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4, 'p5': p5,'p6': p6})
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

def Remove_from_Table(table, name, table_field):  # based on exact matches, not partial
	sqlite_delete_statement = "DELETE from " + table + " WHERE " + table_field + "= :name"
	add_dict_to_sql = {'name': name}
	print("Executing SQL statement: " + sqlite_delete_statement,add_dict_to_sql)
	 
	with db:
		cur.execute(sqlite_delete_statement,add_dict_to_sql)

def check_colour_id_table():
	
	cur.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Colour_Identity' """)
	if cur.fetchone()[0]==1 : 
		print("Table 'Colour_Identity' exists.")
	else:
		cur.execute("CREATE TABLE Colour_Identity (id_Code TEXT, Guild_Name TEXT)")
# 		recreate table and populate
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

def check_decks_table():
	cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='All_Decks' ")
	if cur.fetchone()[0]==1 : 
		print("Table 'All_Decks' exists.")
	else:
		cur.execute("""
			CREATE TABLE All_Decks (
				id_Code TEXT NOT NULL PRIMARY KEY,
				Deck_Name TEXT,
				Colour_ID TEXT,
				Commander TEXT,
				Number_Colours INTEGER,
				Deck_Tier TEXT,
				Ramp INTEGER,
				Draw INTEGER,
				Target_Removal INTEGER,
				Board_Wipe INTEGER
			)
			""")
		print("New 'All_Decks' Table created.")

def check_cards_table():
	cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Cards' ")
	if cur.fetchone()[0]==1 : 
		print("Table 'Cards' exists.")
	else:
		cur.execute("""
			CREATE TABLE Cards (
				Name TEXT NOT NULL PRIMARY KEY,
				Colour_ID TEXT,
				Converted_Mana_Cost INTEGER,
				Card_Type TEXT,
				Is_Permanent TEXT,
				IS_LEGENDARY TEXT,
				Has_ETB TEXT,
				Has_Ramp TEXT,
				Has_Draw TEXT,
				Has_Target TEXT,
				Has_Wipe TEXT,
				Has_Activated TEXT,
				Has_Triggered TEXT,
				Has_Passive TEXT)	""")
		print("New 'Cards' Table created.")

def check_test_matches_table():
	cur.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Test_Matches' """)
	if cur.fetchone()[0]==1 : 
		print("Table 'Test_Matches' exists.")
	else:
		cur.execute("""CREATE TABLE Test_Matches (
				"gm_ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				"Deck_1"	TEXT NOT NULL,
				"Deck_2"	TEXT NOT NULL,
				"Deck_3"	TEXT,
				"Deck_4"	TEXT,
				"Deck_5"	TEXT,
				"Deck_6"	TEXT,
				"Winner"	TEXT,
				"Loser"	TEXT,
				"Turn_number"	INTEGER,
				"Notes"	TEXT)""")
		print("New 'Test_Matches' Table created.")

def check_land_table():
	cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Lands' ")
	if cur.fetchone()[0]==1 : 
		print("Table 'Lands' exists.")
	else:
		cur.execute("""
			CREATE TABLE Lands (
				Name TEXT NOT NULL PRIMARY KEY,
				Colour_ID TEXT,
				Mana INTEGER,
				Has_Additional TEXT
			)
			""")
		print("New 'Lands' Table created.")

def check_creatures_table():
	cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Creatures' ")
	if cur.fetchone()[0]==1 : 
		print("Table 'Creatures' exists.")
	else:
		cur.execute("""
			CREATE TABLE Creatures (
				Name TEXT NOT NULL PRIMARY KEY,
				Creature_Type TEXT,
				Power INTEGER,
				Toughness INTEGER)
			""")
		print("New 'Creatures' Table created.")

def check_spells_table():
	cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Spells' ")
	if cur.fetchone()[0]==1 : 
		print("Table 'Spells' exists.")
	else:
		cur.execute("""
			CREATE TABLE Spells (
				Name TEXT NOT NULL PRIMARY KEY,
				Spell_Type TEXT,
				Has_Healing TEXT,
				Has_Damage TEXT)
			""")
		print("New 'Spells' Table created.")
	
def check_art_ench_table():
	cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Artifacts_Enchantments' ")
	if cur.fetchone()[0]==1 : 
		print("Table 'Artifacts_Enchantments' exists.")
	else:
		cur.execute("""
			CREATE TABLE Artifacts_Enchantments (
				Name TEXT NOT NULL PRIMARY KEY,
				Spell_Type TEXT,
				Activated_Ability TEXT,
				Triggered_Ability TEXT,
				Is_Passive TEXT,
				Description TEXT)
			""")
		print("New 'Artifacts_Enchantments' Table created.")
		
def check_planeswalker_table():
	cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Planeswalkers' ")
	if cur.fetchone()[0]==1 : 
		print("Table 'Planeswalkers' exists.")
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

def scryfall_search_exact(card_name):
	time.sleep(.2)
	getcard = scrython.cards.Named(exact=card_name)
	
	"""Flip cards and double sided cards have 2 sets of oracle text
	Scryfall represents multiface cards as a single object with a card_faces array describing the distinct faces.
	RELEVANT CARD FACE (as well as regular cards) OBJECTS:
	image_uris  -  this returns a dictionary containing links for 'small', 'normal', 'large', 'png', 'art_crop', 'border_crop'  .. based on .. which set?
			'small' is ~ 145 x 200     'normal' is ~ 488 x 680 - this fits to screen on my laptop.    'large' is ~ 670 x 930 - also fits to screen
	loyalty
	mana_cost 
	name
	oracle_text
	power
	toughness
	type_line
	"""
	face1_text = ""
	face2_text = ""
	cardfaces = []
	try:
		face1_text = getcard.oracle_text().lower()
	except:
		cardfaces = getcard.card_faces()
		card1 = cardfaces[0]
		card2 = cardfaces[1]
		face1_text = card1['oracle_text']
		face2_text = card2['oracle_text']
		# print (card1['name'],card1['oracle_text'])
		# print (card2['name'],card2['oracle_text'])
		# print (card1)
		# for oracle_text in cardfaces:
		# 	print (oracle_text)

	
# # # 	 ENTER THE BATTLEFIELD EFFECTS  # # #
	has_etb = 'FALSE'
	search_etb_terms = ['enters the battlefield', 'enter the battlefield', 'into play']
	for terms in search_etb_terms:
		if terms in getcard.oracle_text().lower(): has_etb = 'TRUE'
	
# # # 	 CARD DRAW   # # #		
	has_draw = 'FALSE'
	if 'draw' in getcard.oracle_text().lower(): has_draw = 'TRUE'

# # # 	 TARGETING EFFECTS  (NOT NECESSARILY TARGET REMOVAL) # # #		
	has_target = 'FALSE'
	""" For the time being, this won't take into consideration anything that wouldn't be effected by permanents with
	hexproof or shroud, since they aren't 'targeting' a creature.   Though this could be adapted to also include cards
	with 'Choose' in the text.  However some are trickier to find still...
	
	['You may have Clone enter the battlefield as a copy of any creature on the battlefield']  - Doesn't technically target a creature, but similar effect"""
	
	if 'target' in getcard.oracle_text().lower(): has_target = 'TRUE'

# # # 	 RAMP EFFECTS   # # #	
	has_ramp = 'FALSE'  
	"""[{T}, Sacrifice a black or artifact creature: Add an amount of {B} equal to the sacrificed creature's converted mana cost.]  : Soldevi Adnate IS a ramp creature	
	[{R}:  Add {B} to your mana pool ] is not a ramp creature, just a mana-fixing one.. pretty rare exception though]:  Agent of Stromgald
	plus all those cards that provide treasure tokens or Eldrazi Scion that sacrifice for mana aren't exactly ramp cards either
	"""
	land_names = ['land', 'plains', 'island', 'mountain', 'swamp', 'forest']
	search_ramp_terms = ['Add {C}','Add {W}','Add {U}','Add {B}','Add {R}', 'Add {G}', 'your mana pool', 'add one mana']
	
	for terms in search_ramp_terms:
		if terms in getcard.oracle_text() or terms in getcard.oracle_text().lower() : has_ramp = 'TRUE'
	
	if 'onto the battlefield' in getcard.oracle_text().lower() or 'into play' in getcard.oracle_text():
		for lands in land_names:
			if lands in getcard.oracle_text().lower(): has_ramp = 'TRUE'
			
# # # 	 BOARD WIPES  # # #
	has_wipe = 'FALSE'
	search_wipe_terms = ['destroy all','exile all','destroy each', 'exile each', 'sacrifices the rest', 'destroy the rest', 'damage to each', 'all other', 'each other']
	
	for terms in search_wipe_terms:
		if terms in getcard.oracle_text() or terms in getcard.oracle_text().lower() : has_wipe = 'TRUE'
	
	# cards with overload that destroy or damage or return to hand or exile creatures will trigger as well
	if 'overload' in getcard.oracle_text().lower() and 'all' in getcard.oracle_text().lower():
		if 'destroy' in getcard.oracle_text().lower() or 'exile' in getcard.oracle_text().lower() or 'damage' in getcard.oracle_text().lower() or 'return' in getcard.oracle_text().lower():
			has_wipe = 'TRUE'

# # # 	 TRIGGERED ABILITIES  # # #
	triggered_ability = 'FALSE'
	triggered_ability_terms = ['when', 'whenever']

	for terms in triggered_ability_terms:
		if terms in getcard.oracle_text() or terms in getcard.oracle_text().lower() : triggered_ability = 'TRUE'

# # #    ACTIVATED ABILITIES (MAY OR MAY NOT REQUIRE TAPPING) # # #

	activated_ability = 'FALSE'
	activated_ability_terms = ['only during your', 'activate','{t}:','}:', 'equip ']
	
	for terms in activated_ability_terms:
		if terms in getcard.oracle_text() or terms in getcard.oracle_text().lower() : activated_ability = 'TRUE'	
		
# # #    PASSIVE ABILITIES (MAY OR MAY NOT BE GLOBAL EFFECTS) # # #
	""" This one will be much trickier to filter out via a few search terms... words like 'All' appear on way too many cards
	"You may play lands from your graveyard."  - Crucible of Worlds
	"Creatures you control have haste. " - Fervor
	"All creatures gain Forestwalk" - Whats-his-name
	"All permanents are colorless" - Thran Lens
		
	Equipped creature has defender and "{2}, {T}: Other creatures you control gain trample and get +X/+X until end of turn,
	where X is this creature's power."   - Dragon Throne of Tarkir , Not a Passive card
	"""
	is_passive = 'UNKNOWN'
	# passive_terms = ['']

# # # 	 SUMMARIZE / ADD TO TABLES  # # #

	# base_type = ''
	sub_type = ''
	card_string = ''
	
	print (getcard.type_line())
	if '—' in getcard.type_line():
		card_types = getcard.type_line().split('—')
		# base_type = card_types[0]
		sub_type = card_types[1]
		print (sub_type)

	# if '-' in type_line:
	# 	card_types = type_line.split('—')
	# 	base_type = card_types[0]
	# 	sub_type =  card_types[1]
			
	if 'Planeswalker' in getcard.type_line():
		# print ("Loyalty: " + str(getcard.loyalty()))
		counter = 0
	
	# 	 This part I found annoying, it seems that I don't encounter this error with Planeswalkers oracle text unless I try and print it,
	#    specifically the '-' sign..??   weird
		for letters in range(len(getcard.oracle_text())):	
			try:
				letter = str(getcard.oracle_text()[counter])
				if (letter == '+' or letter == '-') and counter > 10: is_passive = 'LIKELY'
				"""If there is a bit of oracle text before a boost or cost ability, then there is a good chance that the
				Planeswalker has a passive abililty, like the uncommon ones from War of the Spark
				"""
				
				card_string = card_string + letter
				counter += 1
				# print (card_string)
			except (UnicodeEncodeError, IndexError):
				size = len(card_string)
				if counter > 10: is_passive = 'LIKELY'
				
				# Slice string to remove that cursed broken Unicode '\u2212' character ('-') from string
				mod_string = card_string[:size - 1]
				card_string = mod_string + '-'
				# if IndexError: print("Index Error")
				# if UnicodeEncodeError: print("UnicodeEncodeError Error")
		# print (card_string)
			
# # #    PLANESWALKER ABILITIES  # # #    
		boost_ability = 'FALSE'
		cost_ability = 'FALSE'
		ultimate_ability = 'FALSE'
		boost_ability_terms = ['+1:', '+2:','+3:','+4:', '+5:', '+6:', '+7:', '+8:']
		cost_ability_terms = ['-1:', '-2:','-3:','-4:', '-5:', '-6:', '-7:', '-8:', '-9:', '-10:', '-11:', '-12:', '-13:', '-14:']
	
		for terms in boost_ability_terms:
			if terms in card_string: boost_ability = 'TRUE'
		
		count_costs = 0
		for terms in cost_ability_terms:
			if terms in card_string:
				cost_ability = 'TRUE'	 # Won't cost_ability always be true?
				count_costs += 1
		
		if count_costs > 1 : ultimate_ability = 'TRUE'	
		
		if 'can be your commander' in card_string: is_passive = 'TRUE'
		
		insert_planeswalker(getcard.name(), int(getcard.loyalty()), is_passive, boost_ability, cost_ability, ultimate_ability)
	
	# print (getcard.name())
	if 'Creature' in getcard.type_line():
		# print (sub_type)
		insert_creature(getcard.name(), sub_type, getcard.power(), getcard.toughness())
		# print ("Power: " + str(getcard.power()))
		# print ("Toughness: " + str(getcard.toughness()))
	else:
		if 'Artifact' in getcard.type_line() or 'Enchantment' in getcard.type_line() :
			"""card_description isn't intended as a replacement for oracle_text, just personal notes """
			card_description = ""
			
			insert_art_ench(getcard.name(), sub_type, activated_ability, triggered_ability, is_passive, card_description)			
	if 'Land' in getcard.type_line():
		has_additional = 0
		# print (getcard.produced_mana())
	
	if 'sorcery' in getcard.type_line().lower() or 'instant' in getcard.type_line().lower():

		damage_ability = 'FALSE'
		heal_ability = 'FALSE'
		
		damage_ability_terms = ['damage', 'lose life', 'pay life']
		heal_ability_terms = ['heal', 'gain life']
		
		for terms in damage_ability_terms:
			if terms in getcard.oracle_text() or terms in getcard.oracle_text().lower() : damage_ability = 'TRUE'	

		for terms in heal_ability_terms:
			if terms in getcard.oracle_text() or terms in getcard.oracle_text().lower() : heal_ability = 'TRUE'
		
		if 'gain' in getcard.oracle_text().lower() and 'life' in getcard.oracle_text().lower(): heal_ability = 'TRUE'
	
		# print ("Deals Damage: " + damage_ability)
		# print ("Has Healing: " + heal_ability)
		
		insert_spell(getcard.name(), getcard.type_line().upper(), heal_ability, damage_ability)
	# try:
	# print ("Heal/Damage Effect: " + str(getcard.life_modifier()))
	# except:
	# 	pass	
		
	try:
		card_string = getcard.oracle_text()
		# print (card_string)	
	except:
		pass
	
	# print ("Has ETB: " + has_etb)
	# print ("Has Target: " + has_target)
	# print ("Has Draw: " + has_draw)
	# print ("Has Ramp: " + has_ramp)
	# print ("Has Activated Ability: " + activated_ability)
	# print ("Has Triggered Ability: " + triggered_ability)
	# print ("Has Passive Ability: " + is_passive)
	update_card_table(getcard.name(), has_etb, has_target, has_draw, has_ramp, has_wipe, activated_ability, triggered_ability)
		
def update_card_table(name, etb, target, draw, ramp, wipe, activated, triggered):
	sql_update_statement = """UPDATE Cards
	SET Has_Ramp = '""" + ramp + """',
	Has_Target = '""" + target + """',
	Has_ETB = '""" + etb + """',
	Has_Wipe = '""" + wipe + """',
	Has_Draw = '""" + draw + """',
	Has_Activated = '""" + activated + """',
	Has_Triggered = '""" + triggered + """'
	WHERE Name = """ + '"' + name + '"'
				
	print(sql_update_statement)
	cur.execute(sql_update_statement)
	
def import_inventory():
	# import from inventory table CSV file
	latest_inventory = 'MTG Inventory 21-5-4.csv'
	importcount = 0
	with open(latest_inventory, 'r') as csv_file:
		csv_reader = csv.reader(csv_file)
		next(csv_reader)
		
		for line in csv_reader:
			importcount += 1
			try:
				insert_card_partial(line[2], line[15], line[16])
				scryfall_search_exact(line[2])
			except Exception:
				print(line[2],Exception)
				# if 'IndexError' in Exception:
				# 	print('list index out of range on import inventory to sql')
				# print(line[2], line[15], line[16], line[17])
				#Name,  Type,  Cost,  Image URL
			# if importcount > 100 : break
	print(f'{importcount} records checked')
	db.commit()
	cur.execute("SELECT count(*) from Cards")
	result = cur.fetchone()
	print(f'{result} records added to Cards Table')

	"""Card name can then be queried into Scrython for more card info
	Good Samaritan: Don't make more than 5 calls per second!!   .. don't think I'll need to worry too much.
	integrating scryfall will ultimately save a lot of time but I won't want to leave the system to do 1000+ queries at once
	- May 4th run of ~9800 records added ~8200 records and took approximately 12 hours"""

def test_search(card_name):
	getcard = scrython.cards.Named(exact=card_name)
	
	face1_text = ""
	face2_text = ""
	cardfaces = []
	card1images = {}
	card2images = {}
	try:
		face1_text = getcard.oracle_text().lower()
		# card1images = getcard.image_uris()
	except:
		cardfaces = getcard.card_faces()
		card1 = cardfaces[0]
		card2 = cardfaces[1]
		# card1images = card1['image_uris']
		# card2images = card2['image_uris']
		face1_text = card1['oracle_text']
		face2_text = card2['oracle_text']
		print (face1_text)
		print (face2_text)
		# print (card1images['normal'])
		# for oracle_text in cardfaces:
		# 	print (oracle_text)
		
		
def main():
	# CLEAR OLD TABLES IF NECESSARY
	
	#   cur.execute("DROP TABLE IF EXISTS 'Spells'")   
	# print("Removed old 'Artifacts_Enchantments' Table, it's for the best..")

	# scryfall_search_fuzzy('Absolute')
	
	# SEE IF TABLES EXIST

	# check_colour_id_table()
	# check_decks_table()
	# check_cards_table()
	# check_test_matches_table()
	# check_land_table()
	# check_creatures_table()
	# check_spells_table()
	# check_art_ench_table()
	# check_planeswalker_table()

# # # #   COUNT TABLES 
# 	cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table'")
# 	print("Tables Found:" + str(cur.fetchone()[0]))
# 	cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
# 	print("Table :" + str(cur.fetchall()))
	
	# scryfall_search_exact("Jorn, God of Winter // Kaldring, the Rimestaff")
	# test_search("Jorn, God of Winter // Kaldring, the Rimestaff")
	test_search("Callow Jushi")
	
	# import_inventory()
		
	db.commit()
	db.close()
	
if __name__ == '__main__': main()


# # #  THE DIFFERENT INSERT METHODS
	
	#insert_deck(d_id, name, clr_ID , commander, num_clrs, tier, ramp, card_draw, target_removal, board_wipe)
	#insert_planeswalker(name, loyalty, is_passive, boost_ability, cost_ability, ultimate)
	#insert_card(name, clr_ID, cmc, c_type, is_perm, is_legend, has_etb, has_ramp, has_draw, has_target, has_wipe, has_activated, has_triggered, is_passive)
	#insert_card_partial(name, type_line, mana_cost)
	#insert_game(ID, playerlist, winner, loser, turns, notes)
	#insert_art_ench(name, spell_type, activated_ability, triggered_ability, is_passive, description)
	#insert_spell(name, s_type, healing, damage)
	#insert_creature(name, cr_type, power, toughness)
	#insert_land(name, clr_ID, mana, has_additional)
	#insert_guild(code, name)      # This is just a static list of 32 entries
	
# # #  Remove VALUES From THE TABLES
	#Remove_from_Table(table, name, table_field)
	
"""Notes:

Entire inventory cardlist is saved as comma separated values   (approximately 8200 entries)
Name, Type, Cost, Image URL

Type example:  'Creature - Human Shaman'
Cost format examples:  '{3}{W}{U}{B}{R}{G}'
					   '{2W}{2U}{2B}{2R}{2G}'
Image Url example:  'https://deckbox.org/system/images/mtg/cards/96953.jpg'


Cost format will need to be converted to both Colour Code , and also CMC

Convert '{2W}{2U}{2B}{2R}{2G}' to WUBRG ,  CMC:10
'{3}{W}{U}{B}{R}{G}'  to WUBRG, CMC:8

"""