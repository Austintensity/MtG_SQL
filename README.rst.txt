A Work-in-Progress SQLite database to create and manage Magic the Gathering commander decks.
Written by Paul Austin  2021
README Last Updated: 2021-09-08
Thanks to https://scryfall.com/docs/api


####################
HOW TO USE
####################

The frame(s) on the left of the screen are to access the complete list (Names & Colour identity) of created decks (from All_Decks table), view and update certain
deck details and write notes, and find cards in your inventory based on various search criteria.   
  Name
  CMC
  Oracle Text
  Keywords
  Colour Identity
  Card Type
  Power
  Toughness
  Ramp
  Draw
  Target ability
  Broad ability
  Enter the battlefield effect 
  Legendary
   OR you can write your own search parameters for SELECT Name, Mana_Cost, Card_Type WHERE .. statement 
Cards shown in search results can be further filtered down by entering a partial card name and cards can be added to the Main deck or the Sideboard.

Deck Details are updated 
  Deck Name - Something poetic hopefully, and more than just whatever the Commander's name is
  Deck Location (optional) - I usually have a few dozen decks so this keeps track of in which card box the deck can be found
  Deck Tier - ['Primary', 'Secondary', 'Online']
  Deck Status - ['ACTIVE', 'INACTIVE', 'UNASSEMBLED']   -Why does Deck Status 'shout' when Deck Tier doesn't?
  Deck Table - Name of the SQL table of the list of cards included 
  Deck Notes (optional) - Whatever you want, maybe cards to consider for the deck (maybeboard?)  or note which cards in the deck have worked the best, list of tokens the deck uses..?
  Deck ID  - This can be whatever you want, but I like to create mine based on the following legend.  Sorry it isn't alphabetized since it keeps expanding
					'a': aristocrat			'E': Evasion		'P': Populate			'H': Group Hug			
					'A': Artifacts			'G': Graveyard		'S': Sacrifice			'Q': eQuipment
					'b': blink				'I': Infect			'sc': spell copy		'$': buyback
					'B': Battle				'K': Kicker			'T': Tribal				'g': gift
					'c': creatures			'M': Madness		't': stealing			'xc': x-closer spells
					'C': Counters			'm': morph			'U': Untap				'd': deathtouch
					'cs': counterspells		'n': ninjitsu		'W': Word				'&': clone
					'D': Draw				'N': eNchantments	'X': eXtra turns		'R': enRAGE!!
					'L': Land matters							
  
The top frame on the right side is the list of cards included in the main deck, divided up by Creatures, Instants, Sorceries, Artifacts, Enchantments, Planeswalkers, Lands.  The bottom right corner frame is for the decks sideboard, divided up the same way.  Any cards that were listed in the deck, but aren't actually in your inventory will be uncategorized, and the program will not consider that card when counting up all of the stats for the deck.  This data is pulled from the Cards tables and that meta data isn't included in the Grandtable(s) tables.  From within the main program GUI, only cards in your inventory can be added to the deck anyway, and uncategorized cards only get added when importing from a text file.  So changing this would be a low priority.  

You can adjust the quantity of a card in your main deck (but not sideboard) by clicking on that card and then entering a new quantity in the 'Adjust Qty:' box and pressing <Enter>

Selecting a Legendary creature or Commander-eligible Planeswalker that is in your deck and clicking on the 'PROMOTE!!' button will make that card your commander.
Selecting a Legendary creature or Commander-eligible Planeswalker with the Partner Keyword that is in your deck and clicking on the 'Partner' button will make that card your Commander's partner, if that commander also has Partner.  This doesn't check to confirm if the Commander can only partner with a specific card however. 

Main Menu
- Deck
   - New
   - Show Details:  Shows the Frame to update the Deck Details
   - Show Inventory:  Shows the Frame with the card searching tool
   - Open:  Shows the Frame with the list of all created decks, it doesn't open that usual open window you are used to seeing in programs since decks are tables in the MTG.db file and not separate files
   - Save:  Also doesn't prompt you for a file name, or anything else.  It just saves the current deck using the specified Deck Details
- Import
   - Inventory:  Opens a file dialog box for a CSV file from the \data folder and then operates similar to import_inventory() in main.py
   - JSON Data:  Opens a file dialog box for a JSON file from the \data folder and then operates similar to main() in json_load.py

#######################################
CARD DATA IN 2 SETS OF PRIMARY TABLES, WHY?
#######################################

Card data is mostly stored in the Cards_Condensed and GrandtableCondensed tables.
Entries made into Cards_Condensed (and Face_Cards_Condensed) are based on your own card inventory, imported from CSV file that came from deckbox.org.  Most of the fields are always blank for standard users, but currently only need the card name anyway.   
Entries made into GrandtableCondensed (and GrandtableSplitCondensed) tables are based on all 22,000+ English cards from the entirety of Magic's history imported from a large JSON file.  There is a lot of overlapping data between the two sets of tables, but only the tables based on your inventory go through the Regular Expression searches and get the meta data for card searches.
Magic cards come in various different layouts, see https://scryfall.com/docs/api/layouts  
Cards that have 2 sets of rules text (or oracle text in Scrython's vernacular) are on a 'Face_Card' or 'Split' table, this is just a small percentage  (~320 / ~22559) 1.4% as of August 2021, and these cards don't even come out in every new expansion set.

###########################
GETTING NEW JSON DATA
###########################
New bulk card data for every Magic the Gathering card is updated daily on https://scryfall.com/docs/api/bulk-data 
The 'All Cards' file that is approximately 195MB+ will take roughly 1.27GB and you should put it in the \db folder.

Importing JSON data will wipe and rebuild the existing 'Grandtables'

###########################
IMPORTING INVENTORY
###########################
Importing an inventory from a comma separated value file will wipe and rebuild the existing inventory card tables.  

###########################
SAMPLE CSV INVENTORY FILE
###########################

Count,Tradelist Count,Name,Edition,Card Number,Condition,Language,Foil,Signed,Artist Proof,Altered Art,Misprint,Promo,Textless,My Price,Type,Cost,Image URL
1,0,Abandoned Sarcophagus,Commander 2020,236,Mint,English,,,,,,,,$0.00,Artifact,{3},https://deckbox.org/system/images/mtg/cards/2012233.jpg
1,0,Abattoir Ghoul,Innistrad,85,Mint,English,,,,,,,,$0.00,Creature - Zombie,{3}{B},https://deckbox.org/system/images/mtg/cards/222911.jpg
1,0,Abhorrent Overlord,Theros,75,Near Mint,English,,,,,,promo,,$0.00,Creature - Demon,{5}{B}{B},https://deckbox.org/system/images/mtg/cards/373661.jpg

############################
SAMPLE JSON DATA
############################
[	  {"object":"card","id":"0000579f-7b35-4ed3-b44c-db2a538066fe","oracle_id":"44623693-51d6-49ad-8cd7-140505caf02f","multiverse_ids":[109722],"mtgo_id":25527,"mtgo_foil_id":25528,"tcgplayer_id":14240,"cardmarket_id":13850,"name":"Fury Sliver","lang":"en","released_at":"2006-10-06","uri":"https://api.scryfall.com/cards/0000579f-7b35-4ed3-b44c-db2a538066fe","scryfall_uri":"https://scryfall.com/card/tsp/157/fury-sliver?utm_source=api","layout":"normal","highres_image":true,"image_status":"highres_scan","image_uris":{"small":"https://c1.scryfall.com/file/scryfall-cards/small/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979","normal":"https://c1.scryfall.com/file/scryfall-cards/normal/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979","large":"https://c1.scryfall.com/file/scryfall-cards/large/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979","png":"https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979","art_crop":"https://c1.scryfall.com/file/scryfall-cards/art_crop/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979","border_crop":"https://c1.scryfall.com/file/scryfall-cards/border_crop/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979"},"mana_cost":"{5}{R}","cmc":6.0,"type_line":"Creature — Sliver","oracle_text":"All Sliver creatures have double strike.","power":"3","toughness":"3","colors":["R"],"color_identity":["R"],"keywords":[],"legalities":{"standard":"not_legal","future":"not_legal","historic":"not_legal","gladiator":"not_legal","pioneer":"not_legal","modern":"legal","legacy":"legal","pauper":"not_legal","vintage":"legal","penny":"legal","commander":"legal","brawl":"not_legal","duel":"legal","oldschool":"not_legal","premodern":"not_legal"},"games":["paper","mtgo"],"reserved":false,"foil":true,"nonfoil":true,"oversized":false,"promo":false,"reprint":false,"variation":false,"set":"tsp","set_name":"Time Spiral","set_type":"expansion","set_uri":"https://api.scryfall.com/sets/c1d109bc-ffd8-428f-8d7d-3f8d7e648046","set_search_uri":"https://api.scryfall.com/cards/search?order=set\u0026q=e%3Atsp\u0026unique=prints","scryfall_set_uri":"https://scryfall.com/sets/tsp?utm_source=api","rulings_uri":"https://api.scryfall.com/cards/0000579f-7b35-4ed3-b44c-db2a538066fe/rulings","prints_search_uri":"https://api.scryfall.com/cards/search?order=released\u0026q=oracleid%3A44623693-51d6-49ad-8cd7-140505caf02f\u0026unique=prints","collector_number":"157","digital":false,"rarity":"uncommon","flavor_text":"\"A rift opened, and our arrows were abruptly stilled. To move was to push the world. But the sliver's claw still twitched, red wounds appeared in Thed's chest, and ribbons of blood hung in the air.\"\n—Adom Capashen, Benalish hero","card_back_id":"0aeebaf5-8c7d-4636-9e82-8c27447861f7","artist":"Paolo Parente","artist_ids":["d48dd097-720d-476a-8722-6a02854ae28b"],"illustration_id":"2fcca987-364c-4738-a75b-099d8a26d614","border_color":"black","frame":"2003","full_art":false,"textless":false,"booster":true,"story_spotlight":false,"edhrec_rank":4981,"prices":{"usd":"1.22","usd_foil":"5.00","eur":"0.32","eur_foil":"1.88","tix":"0.02"},"related_uris":{"gatherer":"https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=109722","tcgplayer_decks":"https://decks.tcgplayer.com/magic/deck/search?contains=Fury+Sliver\u0026page=1\u0026utm_campaign=affiliate\u0026utm_medium=api\u0026utm_source=scryfall","edhrec":"https://edhrec.com/route/?cc=Fury+Sliver","mtgtop8":"https://mtgtop8.com/search?MD_check=1\u0026SB_check=1\u0026cards=Fury+Sliver"}}
]  

Breath-taking and majestic, isn't it?


#####################
THE PROJECT FILES
#####################

################
MTG_MAIN.PY
################

mtg_main.py handles queries to Scryfall to fetch raw card data and calls Regular Expression functions from mtg_regex.py to interpret the card information to see what card meta sub-categories ('draw', 'ramp', 'target removal') apply to it.  Main program then calls functions from mtg_sql.py to add all relevant card data to the main SQL tables  (Cards_Condensed, Face_Cards_Condensed)

Running mtg_main.py opens the GUI (gui_class.py)

Other functionality: 
  import_inventory()   - Process latest inventory csv file from deckbox.org and run scryfall_search_exact() to add all eligible cards to
	populate the 'Cards'/'Cards_Condensed' and 'Face_Cards'/'Face_Cards_Condensed', and subsequently the 'Creatures', 'Lands',
	'Spells','Planeswalkers' tables get filled as well.
	- Returns nothing

  get_colour_id(mana_cost)   - Simply checks for each color letter in a 'mana_cost'   (Usually it is better to use a cards '.color_identity()' instead)
	- Returns: string 'clr_id'   


################
GUI_CLASS.PY
################

gui_class.py contains all the GUI functions, reads and writes to the SQL card and deck tables, and the deck handling functionality.   You can search by card name or various card meta data that is already added to the card tables to filter and preview cards to add to a new or existing deck.

Running gui_class.py effectively does nothing, no main() function included

Other functionality:
  import_inventory_gui(self)  - Similar to import_inventory(), user selects a CSV inventory file from the \data folder and rebuilds the Cards_Condensed, Face_Cards_Condensed tables

  import_json_gui(self)   - Similar to main() from json_load.py, user selects a JSON card database from the \data folder and rebuilds the GrandtableCondensed, GrandtableSplitCondensed tables

  count_cards(self) - Counts all of the Creatures, Instants, Sorceries, Artifacts, Enchantments, Planeswalkers, Lands are in a main deck (and the sideboard).  Also counts up all mana symbols in the main deck and updates display by running show_pie_chart(self)  

  show_pie_chart(self) - Uses matplotlib.pyplot to plot mana symbol data gathered from count_cards(self) 


################
MTG_SQL.PY
################

mtg_sql.py handles most of the functions using SQL queries.   Creates and checks to make sure all the required tables are created.  All functions to create or add to an existing SQLite table is included here.  
	Steps for adding a deck
	1. Running import_deck_fromtxt() to import a deck list (exported from deckbox.org, etc) and give a name to that table, which will be referred to as deck_list 
	2. Running the calculate_deck(deck_list)  and get the deck's stats
	3. Running create_new_deck() to assemble the data and add it to All_Decks table  
	
Running mtg_sql.py effectively does nothing.  main() function included, but just for testing and rebuilding the deck tables for all the decklists exported from deckbox.org

Other functionality:
  import_deck_fromtxt(textfile, deck_list) - Opens the specified text file and creates a new SQL table 
 
  calculate_deck(deck_list)  -  Taking data from the deck_list and counting up all the ramp and draw cards, etc
    calls handle_five_things()
	returns: count of all board wipes, draw cards/engines, ramp cards, targeting cards, etb cards, lands, and average converted mana cost, or 'mana value') 
  
  create_new_deck() gets the commander (and partner)'s colour identity and calls insert_deck() to add to 'All_Decks' table 

  check_cardref(card_name)  - Check the 'Cardref' table to see whether the data for a particular card will be in the Cards/Cards_Condensed table or Face_Cards/Face_Cards_Condensed 

  handle_five_things(sql_cursor, qty, current_wp, current_dr, current_rmp, current_tg, current_etb, current_land, current_cmc) - Called by calculate_deck() method, this will (ironically) takes 9 parameters and review the fetch data from the sql_cursor and increment the fields, and returns new updated counts of cards for board wipes, card draw, mana ramp, target removal, enter the battlefield 'etb' effects, lands count, and total converted mana cost (to calculate average)

List of SQL Tables
  All_Decks - List of decks, who the commander/partner is, how many of each type of card is in them
  Cardref - Whether a card's data is stored in the Cards_Condensed table or Face_Cards_Condensed table
  Cards_Condensed - Card data from Scryfall queries for each single-sided card in [deckbox.org exported] inventory CSV file, however doesn't use Row_ID so duplicate entries are ignored
  Face_Cards_Condensed   - Card data from Scryfall queries for each Split/Double-sided card in [deckbox.org exported] inventory CSV file
  Test_Matches - Created incase you wanted to keep a database of all the test games, which for me isn't nearly enough test games.   Might be handy for when you love pitting your decks against each other 
  Lands - How much mana generated, which colours, and if there are any other activated abilities on the card
  Creatures - Creature Type 'tribe', converted mana cost, power, toughness, keywords
  Spells - Instant/Sorcery, how much life gained/damage dealt  
  Planeswalkers  - Starting Loyalty counters, whether or not it has any passive abilities, and the amount of counters added or removed for Boost_Ability, Cost_Ability, and their Ultimate (if they have one)  - Please note that the occasional planeswalker with 2 boost abilities ['Nissa, Worldwaker', 'Saheeli, the Gifted'] will have their 2nd Boost_Ability in the Cost_Ability slot
  GrandtableCondensed - Raw Card data from JSON import (single-sided cards)  , no Row_ID. No duplicates.
  GrandtableSplitCondensed - Raw Card data (Split/Double-sided card) from JSON import. No Row_ID. No duplicates.

  Cards - Card data from Scryfall queries for each single-sided card in [deckbox.org exported] inventory CSV file, uses Row_ID and there are duplicate entries based on card reprints, or if you own a near mint copy of a card and also a heavily played of the same card  - This isn't really being used right now but keeping it around incase I want to get into more in depth inventory management and not just deck management
  Face_Cards  - Card data from Scryfall queries for each Split/Double-sided card in [deckbox.org exported] inventory CSV file, uses Row_ID   
  Grandtable - Raw Card data from JSON import (single-sided cards) , uses Row_ID so there are duplicate entries based on card reprints - Also isn't being used right now, and may in fact be ultimately pointless
  GrandtableSplit - Raw Card data from JSON import (Split/Double-sided card) , uses Row_ID so there are duplicate entries based on card reprints - Maybe useless
  Colour_Identity - Colour_Identity and Guild_Name  - This one isn't really being used right now
	
################
MTG_REGEX.PY
################

mtg_regex.py handles Regular Expressions (RegEx / RegExp) and reading a card's rules text ('.oracle_text()') and determining what catagories the card falls under

Please note that there are still a few false positives with the RegEx searches.

Running mtg_regex.py effectively does nothing, no main() function included

Currently used in getting card data for:
  Mana ramp
  Mana colours (usually colour identity, but not necessarily)
  Card draw
  Enter the battlefield effects (etb):  Most etb effects are Triggered abilities, 
  Target 'Removal': ('Destroy', 'Exile', 'Return', 'put counters on', etc) 
  Keywords:  'Haste'; 'Protection from Red'; etc
  Triggered abilities: (During, Whenever, After, At the end of .. phase, )  
  Activated abilities: (usually requiring either tapping and/or mana cost)
  Amount of life gained/lost 
  Counting Planeswalkers activated abilities: (boost abilities {+X}  / cost abilities {-X})
  Counting Planeswalkers passive abilities:  (".. can be your commander")
  Board Wipes or other broad effects ('each', 'all', 'all other', 'each other', 'the rest')

################
JSON_LOAD.PY
################

json_load.py handles the importing of the full card database JSON file from https://scryfall.com/docs/api/bulk-data, and add the relevant card data to the GrandtableCondensed/GrandtableSplitCondensed tables and is intended to be run as a separate file, the import function is mimicked and accessed through the menu in GUI_CLASS.PY as well, except it prompts you for the JSON filename, where this file just imports a specified file.  

Running json_load.py clears the existing Grandtable(s) and rebuilds them

Based on the card's layout, it will be processed by one of the 3 functions.
  Single_Sided_Card_JSON(the_card)  - Typical one sided MTG Card
  Split_Card_JSON(the_card)  - Cards with two names, two sets of oracle_text and one card image 
  Double_Faced_Card_JSON(the_card)   - Double-sided cards with two names, two sets of oracle_text and two card images 

Calls insert_card_from_JSON() and insert_splitcard_from_JSON() functions from mtg_sql.py


################
MORE TO COME
################

Updates as I can make them.  Just a few things on my TO DO list..

  A broader Advanced Search window with more categories and some customizable options to quicker find the cards your deck
is looking for
  Make the program window objects scale/shift to the window size, scrollbars if necessary
  Direct deck importing via copy/paste instead of a saved text file on your computer, exporting to a text window as well
  Make the table columns sortable
  Plans to track card inventory quantities, as if managing a physical inventory rather than a virtual one.  - This will get more complicated if it starts tracking card expansions/card set numbers/card condition/which version of a card is in which deck...depends how far I end up taking it
  and more..
  