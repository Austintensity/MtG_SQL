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
   
import time
import sqlite3
import csv
import sys
import scrython
import os
from pathlib import Path
from mtg_classes import *
import mtg_regex
import mtg_sql
import gui_class

""" convert_manawords (this is used for draw as well)  Changes to how it will be added to SQL tables  """
convert_manawords = {
    'one' : '1',
    'two' : '2',
    'three' : '3',
    'four' : '4',
    'five' : '5',
    'six' : '6',
    'seven' : '7',
    'eight' : '8',
    'nine' : '9',
    'ten' : '10',
    'x' : 'X',
    'an amount of ' : 'X',
    'as many' : 'X',
    'that many' : 'X',    
    'a' : '1',
    'an additional' : '+1'
    }

def select_case_layout(cardtype, the_card):
    """Based on layout of the card, this will consult the dictionary for which function to run
    Returns:  RUNNING the appropriate function
    """
    execute_function = convert_layout.get(cardtype, "Invalid type")
    return execute_function(the_card)

def make_list(string_in):
    split_string = string_in.split(" ")
    if split_string[len(split_string)-1] == "": split_string.pop()
    return split_string

def check_oracle_text(oracletext):
    """Searching the oracle_text for that cursed broken Unicode '\u2212' character that Python's console can't print,
    and replace it with an ordinary minus sign, line breaks are removed as well
    Returns: String 'card_string'  """
    card_string = oracletext
    if '−' in oracletext: card_string = oracletext.replace('−', '-')
    if '\n' in card_string: card_string.replace('\n', '     ')
    
    return card_string

def rebuild_list(list_to_fix):
    """Parameter:   list_to_fix:  A list that was broken down character by character to put back.   Returns:  String 'rebuildstring'
    """
    rebuildstring = ""
    for x in list_to_fix:
        rebuildstring = rebuildstring + x
    return rebuildstring

def get_colour_id(mana_cost):
    """Simply checks for each color letter in 'mana_cost'   Returns: string 'clr_id'
    """
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

"""### ORACLE TEXT SEARCHING ###   START """

def ETB_Search(oracletext, card_type, keywords):
    """Runs a basic oracle text search for usual etb lexicon.  If so, then runs regex_get_ETB() to analyse further.
    Returns:   list 'etb'
    """
    has_etb = ''
    search_etb_terms = ['enters the battlefield', 'enter the battlefield']
    for terms in search_etb_terms:
        if terms in oracletext.lower(): has_etb = 'TRUE'
    if has_etb == 'TRUE' :
        etb = mtg_regex.regex_get_ETB(oracletext, card_type, keywords)
    else:
        etb = "-"
    return etb

def Draw_Search(oracletext):
    """Simple enough, if the card might have a draw ability, RUNS regex_get_draw() is run to look further
    Returns:  string: 'has_draw'  - usually '-' for N/A, or maybe 1,2 or 'X'
    """
    has_draw = ''
    if 'draw' in oracletext:
        has_draw = mtg_regex.regex_get_draw(oracletext)
    else:
        has_draw = '-'
    return has_draw
            
def Target_Search(oracletext, card_type, keywords):
    """REGEX oracle text search check for usual 'target' lexicon, then goes through list of target types to see if those
    were found in/around the 'target' text.   
    Parameters: oracletext:  Cards oracle text, having run through check_oracle_text()
                card_type:   Card type from MTG_Cards/MTG_Face_Cards   {'Creature', 'Sorcery', etc}
                keywords:    Keywords for a card, to check for 'Hexproof' and 'Shroud' which would have "target" be in the explanation text anyway
    Returns:  list: 'has_target'
    **This was partially on the MTG_Regex page under regex_get_target() but I was having issues so it was all combined and moved here

     For the time being, this won't take into consideration anything that wouldn't be effected by permanents with
    hexproof or shroud, since they aren't 'targeting' a creatumtg_sql.insert_   Though this could be adapted to also include cards
    with 'Choose' in the text.  However some are trickier to find still...
    
    ['You may have Clone enter the battlefield as a copy of any creature on the battlefield']  - Doesn't technically target a creature, but similar effect"""
    
    if 'target' in oracletext.lower():
        # has_target = regex_get_target(oracletext, card_type, keywords)
        target = ""
        keywords = rebuild_list(keywords)
        regex_target_terms = ['destroy', 'damage', 'return', 'exile', 'flip', 'discard', 'shuffle', 'enchant', 'haunt', 'reveal', 'exchange',
                              'copy', 'life', 'draw', 'attach', 'copies', 'attack','block', 'sacrifice', 'token'] 
        pattern = mtg_regex.re.compile(mtg_regex.regex_searchmode['target_filter'])    
        matches = pattern.finditer(oracletext)
        for match in matches:
            startgrab = min(match.span())
            endgrab = max(match.span())
            matchfound = oracletext[startgrab:endgrab]
            # if 'gets' in matchfound: target = target + ""
            for terms in regex_target_terms:
                if terms in matchfound:
                    if len(target) > 2:
                        target = target + terms.capitalize() + " "
                    else:
                        target = terms.capitalize() + " "
        
        if mtg_regex.re.findall(mtg_regex.regex_etb_modes['mill'], oracletext, mtg_regex.re.IGNORECASE): target = target + "Mill "
        
        for filters in mtg_regex.regex_target_modes:
            # print (re.findall(regex_target_modes[filters], oracletext, re.IGNORECASE))
            if mtg_regex.re.findall(mtg_regex.regex_target_modes[filters], oracletext, mtg_regex.re.IGNORECASE):
                # print ("found ", filters)
                target = target + filters.capitalize() + " "
                
        if "can't be the target of spells or abilities" in oracletext.lower() or "can't be the targets of spells or abilities" in oracletext.lower()   : target = target + "Shroud "
        if 'shroud' in oracletext.lower(): target = target + "Shroud "
        if 'hexproof' in oracletext.lower(): target = target + "Hexproof "
        if 'mutate' in keywords.lower(): target = target + "Mutate "        
        if 'heroic' in keywords.lower(): target = target + "Heroic "
        if 'enchant' in keywords.lower() or 'aura' in card_type.lower():
            if 'Enchant' in target:
                pass
            else:
                target = target + "Enchant "            
            
        if target == "" : target = "Other"
        """Converting the string to a list and removing blank entries"""
        final_target = set(target.split(" "))
        filter_list = filter(lambda x: x != "", final_target)
        has_target = list(filter_list)
    else:
        has_target = '-'
    # print (has_target)
    return has_target

def Ramp_Search(oracletext, card_type):
    """Runs a basic oracle text search to see if it is possibly a ramp card.  If so, then runs regex_get_ramp() to analyse further.
    *Lands don't count as ramp cards
    Returns:  list   ex ['Mana_Dork', 'Fetch_Land']
    """
    
    has_ramp = ''  
    """[{T}, Sacrifice a black or artifact creature: Add an amount of {B} equal to the sacrificed creature's converted mana cost.]  : Soldevi Adnate IS a ramp creature    
    [{R}:  Add {B} to your mana pool ] is not a ramp creature, just a mana-fixing one.. pretty rare exception though]:  Agent of Stromgald
    plus all those cards that provide treasure tokens or Eldrazi Scion that sacrifice for mana aren't exactly ramp cards either
    """
    land_names = ['land', 'plains ', 'island ', 'mountain ', 'swamp ', 'forest ']
    search_ramp_terms = ['add {c}','add {w}','add {u}','add {b}','add {r}', 'add {g}', 'add {1}', 'add {2}', 'add {3}', 'add {4}', 'add one mana','add two mana','add three mana', 'your mana pool', 'add one mana']
    

    for terms in search_ramp_terms:
        if terms in oracletext or terms in oracletext.lower() : has_ramp = 'TRUE'
    
    if 'onto the battlefield' in oracletext.lower() or 'into play' in oracletext:
        for lands in land_names:
            if lands in oracletext.lower(): has_ramp = 'TRUE'
            
    if has_ramp == 'TRUE':
        ramp_abilities = mtg_regex.regex_get_ramp(oracletext, card_type)
    else:
        ramp_abilities = '-' 
    if 'land' in card_type.lower() : ramp_abilities = '-'

    if (len(ramp_abilities) == 0 and 'treasure token' in oracletext) or (ramp_abilities == "" and 'create a treasure' in oracletext):
        # print ("CAPTURED TREASURE!  Converted [] ramp cards back to ['Treasure']")
        ramp_abilities = ['Treasure']
    if ramp_abilities == "": ramp_abilities = "Other"
    final_ramp = set(ramp_abilities.split(" "))
    filter_list = filter(lambda x: x != "", final_ramp)
    # print ("Cramp'n for Ramp'n: ", list(filter_list))
    # print (ramp_abilities)
    # print (final_ramp)
    # print ((lambda x: x != "", final_ramp))
    
    # return list(filter_list)
    return ramp_abilities            
                
def Wipe_Search(oracletext, keywords):
    """Runs a basic oracle text search to see if it is possibly a board wipe card.  If so, then runs regex_get_wipe() to analyse further
    Returns:  list   ex ['Shuffle', 'Exile']
    """
    has_wipe = ''
    search_wipe_terms = ['destroy all','exile all','destroy each', 'exile each', 'return each', 'sacrifices the rest', 'destroy the rest', 'damage to each', 'all other', 'each other', ' every ']
    keywords = rebuild_list(keywords)
    for terms in search_wipe_terms:
        if terms in oracletext or terms in oracletext.lower() : has_wipe = 'TRUE'        
            
    if has_wipe == 'TRUE' : 
        has_wipe = mtg_regex.regex_get_wipe(oracletext, keywords)
        # print (has_wipe)
        
        # "Most of these are towels, be wrong once" - Frank Cross, Scrooged
        if has_wipe[0] == 'Changeling' or (has_wipe[0] == 'Other' and 'changeling' in keywords.lower()):
            has_wipe = '-'
    else:
        has_wipe = '-'
    # print (has_wipe)
    return has_wipe

def Trigger_Search(oracletext, keywords):
    """Simple text search for usual marks of triggered abilities.  Single sided cards
    Returns: triggered_ability  {'Yes' , 'No'}  
    """
    triggered_ability = '-'
    triggered_ability_terms = ['when', 'whenever']
    
    for terms in triggered_ability_terms:
        if terms in oracletext or terms in oracletext.lower() : triggered_ability = mtg_regex.regex_get_triggered(oracletext, keywords)
    
    # print (triggered_ability, type(triggered_ability))
    return (triggered_ability)

def Activated_Search(oracletext, keywords):  
    """Simple text search for usual marks of activated abilities.  Single sided cards
    Returns: String  'activated_ability'
    """
    activated_ability = '-'
    activated_ability_terms = ['only during your', 'activate','{t}:','}:', 'equip ', 'madness ']
    
    for terms in activated_ability_terms:
        if terms in oracletext or terms in oracletext.lower() : activated_ability = mtg_regex.regex_get_activated(oracletext, keywords)

    # print (activated_ability)
    return (activated_ability)

def Legendary_Search_Faces(face1_type, face2_type):
    """Simply compares the card type of both faces of the card and returns whether
    it's legendary in the format of 'Y:N' or 'N:N' .  The opposite face of the card will
    always have the palindrome of this
    """
    is_legend = 'N:'
    legend_terms = ['legend', 'legendary','elder dragon']
    foundflag = "N"
    for terms in legend_terms:
        if terms in face1_type.lower() : is_legend = 'Y:'
        if terms in face2_type.lower() : foundflag = 'Y'            
    is_legend = is_legend + foundflag
    return (is_legend)

"""### ORACLE TEXT SEARCHING ###   END """

def Land_handle(name, oracletext, clr_ID):
    """Processes card data related to Lands
    Parameters:   name:  Official card name
            oracletext:  Oracle text of the card, having run through check_oracle_text()
                clr_ID:  card's color identity, (counts front and back)  ex  ['B', 'G', 'U']
    Returns: Nothing   RUNS insert_land() to add card (or face) data to 'Lands' table
    """
    greatest_mana = 0
    use_mana = 0
    x_found = 'FALSE'
    """REGEX calls to determine how many activated abilities with regex_get_aac()
    and colours of mana generated with regex_get_mclr()  and amount of mana with regex_get_mv()
    """
    act_abilities = mtg_regex.regex_get_aac(oracletext)
    colors = []
    colors = mtg_regex.regex_get_mclr(oracletext)
    if colors is None: colors = {'C'}

    for findmodes in mtg_regex.regex_searchmode:
        if 'mana' in findmodes:
            found_mana = mtg_regex.regex_get_mv(mtg_regex.regex_searchmode[findmodes],oracletext)
            if found_mana is None:
                use_mana = 0
                found_mana = 0
            else:
                try:
                    use_mana = convertmanawords[found_mana]
                except:
                    use_mana = found_mana
                
            if use_mana == 'X' or "add x " in oracletext.lower() or " x mana" in oracletext.lower():
                greatest_mana = 'X'
                x_found = 'TRUE'
                break
            try:
                if use_mana > greatest_mana: greatest_mana = use_mana
            except:    
                if int(use_mana) > greatest_mana: greatest_mana = int(use_mana)

    if not clr_ID: clr_ID.append('C')

    """If a land can produce a variable amount of mana, especially big Honky Muffuzz like Cabal Coffers,
    it is identified as 'X' in the table
    """
    if x_found == 'TRUE':
        mtg_sql.insert_land(name, clr_ID, 'X', str(colors), act_abilities)
    else:
        mtg_sql.insert_land(name, clr_ID, greatest_mana, str(colors), act_abilities)

def Spell_handle(name, oracletext, spelltype):   # REGEX is doing all the heavy lifting on this one
    heal_ability = mtg_regex.regex_get_lifegains(oracletext)
    damage_ability = mtg_regex.regex_get_dmggains(oracletext)
    mtg_sql.insert_spell(name, spelltype, heal_ability, damage_ability)

def Planeswalker_handle(name, oracletext, loyalty):
    """Processes card data related to Planeswalkers
    Parameters:   name:  Official name of card
            oracletext:  Oracle text of the card, having run through check_oracle_text() to deal with
                         that pesky character the console doesn't like
               Loyalty:  Planeswalker's starting loyalty value
    Returns: Nothing  RUNS regex_get_pcosts() , regex_get_pboosts() , regex_get_ppa to count +X abilities, -X abilities
    and determine if there are any passive abilities
    RUNS insert_planeswalker()  to add card (or face) data to Planeswalker Table
    """
    boost_ability = 'FALSE'
    boost_count = 0
    cost_ability = 'FALSE'
    ultimate_ability = 'FALSE'
    is_passive = 'FALSE'
    count_costs = 0
    high_cost_ability = 0
    get_boost = mtg_regex.regex_get_pboosts(oracletext)
    boost_count = len(get_boost)
    """Counting and parsing out the 'boost' abilities that increase Planeswalker's loyalty
    """
    if boost_count == 0:
        pass  # I wrote the option in as a placeholder
    elif boost_count == 1:
        boost_ability = str(get_boost)
    elif boost_count == 2:
        boost_ability = str(get_boost[0])
        boost_ability2 = str(get_boost[1])
    elif boost_count == 3:   # not sure this option will ever exist..
        boost_ability = get_boost[0]
        boost_ability2 = get_boost[1]
        boost_ability3 = get_boost[2]

    get_cost_ability = mtg_regex.regex_get_pcosts(oracletext)
    """Counting and parsing out the 'cost' abilities that spend loyalty points
    """
    count_costs = len(get_cost_ability) 
    if count_costs == 0:
        pass
    elif count_costs == 1:
        cost_ability = str(get_cost_ability)
    elif count_costs == 2:
        cost_ability = get_cost_ability[0]
        high_cost_ability = get_cost_ability[1]
    elif count_costs == 3:   # not sure this option will ever exist..
        cost_ability = get_cost_ability[0]
        cost_ability2 = get_cost_ability[1]    
        high_cost_ability = get_cost_ability[2]
        
    if count_costs > 1 :
        ultimate_ability = 'TRUE'
    else:
        if cost_ability == "X" : ultimate_ability = 'TRUE'
        
    """ Finally a series of checks to determine if the Planeswalker has an 'ultimate ability'
    If a Planeswalker has 2 or more cost abilities, than the greater cost is the ultimate
    If a Planeswalker has 1 cost abiliity that costs more than the starting Loyalty, it is considered 'ultimate'
    
    """
    if loyalty != 'X' and cost_ability != 'X':
        try:
            if int(cost_ability) > int(loyalty): ultimate_ability = 'TRUE'
        except:
            # print ("costability:", type(cost_ability), cost_ability, " loyalty: ", type(loyalty), loyalty)
            if cost_ability > loyalty : ultimate_ability = 'TRUE'
    
    high_cost_ability = "-"+str(high_cost_ability)
    if high_cost_ability == "-0" : high_cost_ability = "-"
    
    cost_ability = "-"+str(cost_ability)
    cost_ability = cost_ability.replace("['","")
    cost_ability = cost_ability.replace("']","")

    """REGEX search to find out how much oracle text there is before the activated abilities are listed,
    these and commanders with 'This Planewalker can be your commander' in the oracle text (usually after the
    activated abilities)
    """
    if 'can be your commander' in oracletext.lower():
        is_passive = 'TRUE'
    else:
        is_passive = mtg_regex.regex_get_ppa(oracletext)

    """The number of boost abilities and cost abilities will determine how it gets added to the table w insert_planeswalker().
    Right now there are a couple PW with 2 boost abilities and the 2nd one is occupying the 1st Cost column
    I know this isn't very eloquent, I hope* to get around to it later
    """
    if boost_count == 0:
        if ultimate_ability == 'TRUE' :
            if count_costs == 1:
                mtg_sql.insert_planeswalker(name, loyalty, is_passive, "-", cost_ability, high_cost_ability)
            elif count_costs == 2:
                mtg_sql.insert_planeswalker(name, loyalty, is_passive, "-", cost_ability, "-")
        else: 
            mtg_sql.insert_planeswalker(name, loyalty, is_passive, "-", cost_ability, "-")
    elif boost_count == 1:
        boost_ability = "+" + str(boost_ability)
        boost_ability = boost_ability.replace("['","")
        boost_ability = boost_ability.replace("']","")
    
        if ultimate_ability == 'TRUE' :
            if count_costs == 1: 
                mtg_sql.insert_planeswalker(name, loyalty, is_passive, boost_ability, "-" , cost_ability)
            else:
                mtg_sql.insert_planeswalker(name, loyalty, is_passive, boost_ability, cost_ability, high_cost_ability)
        else:
            mtg_sql.insert_planeswalker(name, loyalty, is_passive, boost_ability, cost_ability, "-")
    elif boost_count == 2:  # has 1 or more boost abilities and 1 cost ability, if it has 2 boost abilities, than the cost ability is considered the ultimate
        boost_ability = "+" + str(boost_ability)
        boost_ability = boost_ability.replace("['","")
        boost_ability = boost_ability.replace("']","")
        boost_ability2 = "+" + str(boost_ability2)
        boost_ability2 = boost_ability2.replace("['","")
        boost_ability2 = boost_ability2.replace("']","")
        mtg_sql.insert_planeswalker(name, loyalty, is_passive, boost_ability, boost_ability2, cost_ability)
    
def import_inventory():
    """Process latest inventory csv file from deckbox.org and run scryfall_search_exact() to add all eligible cards to
    populate the 'Cards'/'Cards_Condensed' and 'Face_Cards'/'Face_Cards_Condensed', and subsequently the 'Creatures', 'Lands',
    'Spells','Planeswalkers' tables get filled as well.
    Timed process, with scryfall query delay setting of .05, full inventory import takes approximately ... 55 min 52 sec (8-24-20218)
    
    returns nothing
    
    """
    # import from inventory CSV file, exported from deckbox.org
    begin_inv_time = time.time()
    
    Current_Folder = os.path.dirname(os.path.abspath(__file__)) 
    Root_Folder = Path(Current_Folder).parent
    data_folder = Root_Folder / "db"
    latest_inventory = data_folder / "MTG Inventory 21-8-18.csv"

    # print ("Inventory import start time: ", time.localtime(begin_inv_time))
    # latest_inventory = data_folder / 'MTG Inventory 21-8-18.csv'  # this is the same is the 21-7-15.csv file but has bosium strip and lim-dul's crap removed 
    # latest_inventory = data_folder / 'tempventory.csv'
    # latest_inventory = data_folder / 'MTG Inventory - test.csv'
    importcount = 0
    # importignorecount = 0
    with open(latest_inventory, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for line in csv_reader:
            importcount += 1
            """# basically using the try block for weird things like Bösium 'BÃ¶sium' Strip
            https://www.compart.com/en/unicode/U+00F6#:~:text=Unicode%20Character%20%E2%80%9C%C3%B6%E2%80%9D%20(U%2B00F6)
            U+00F6   or U+00D6   ö:  '\xf6'    û: '\xfb'     'Ã¢'
                """
            try:
                search_this = line[2].replace("ö","o")
                search_this = search_this.replace("Ã¶","o")
                search_this = search_this.replace("Ã¢","a")
                search_this = search_this.replace("û","u")
                search_this = search_this.replace("Ã»","u")
                scryfall_search_exact(search_this)
            except Exception as e:
                print("exception error occured importing inventory for ",line[2])
                importcount -= 1
        
    print(f'{importcount} records checked')
    # print(f'{importignorecount} records skipped')
    db.commit()
    
    end_inv_time = time.time()
    run_time = end_inv_time - begin_inv_time

    # print ("Import end time: ", time.localtime(end_inv_time))
    print(f'{importcount} records added to Cards & Face_Cards Tables')

    print ("Import Runtime :", round(run_time,2), " seconds")
    """Card name can then be queried into Scrython for more card info
    Good Samaritan: Don't make more than 5 calls per second!!   .. don't think I'll need to worry too much.
    integrating scryfall will ultimately save a lot of time but I won't want to leave the system to do 1000+ queries at once
    - May 4th run of ~9800 records added ~8200 records and took approximately 12 hours
    - July 6th run of similar records only took ~90 minutes
    - delay of .1 on test inventory upload (July 12) 196 records in 59.2 seconds  3.32 calls/sec
    - delay of .04 for 4.87 calls/sec
    """

"""### CARD LAYOUT HANDLING ###  START """
def Ignore_Card(the_card):  # Art Series, Schemes, Vanguards, all that brick a brack
    # importignorecount = importignorecount + 1
    print ("Skipped card: ", the_card['name'])

def Single_Sided_Card(the_card):
    """ Used for processing cards of the following layouts:
    'normal' , 'token' ,  'meld'  ,  'saga' ,    'leveler' ,    'host' ,'augment',    'emblem'
    Returns nothing  RUNS insert_card() to add to 'Cards' and 'Cards_Condensed' tables
    Creates instance of MTG_Cards() class
    Determines  keywords, {'etb', 'ramp', 'draw', 'target', 'wipe', 'activated' , 'triggered'} abilities for single sided cards
    """
    card_name = the_card.name()
    search_card = MTG_Cards(card_name, the_card.layout(), the_card.color_identity(), the_card.mana_cost(), mtg_regex.regex_get_cmc(the_card.mana_cost()), the_card.type_line(), "", 'No', 'etb', 'ramp', 'draw', 'target', 'wipe',
        'activated', 'triggered', 'image_uri', check_oracle_text(the_card.oracle_text()))

    if not search_card.clr_ID : search_card.clr_ID.append ('C')

    try:
        search_card.image_url= the_card.image_uris()['normal']
    except:
        # Enchantment - Class card types use RegEx to find the image link instead
        search_card.image_url = mtg_regex.regex_get_image(str(the_card.__dict__.items()))

    try:
        search_card.keywords = mtg_regex.regex_get_keywords(str(the_card.__dict__.items()))
    except:
        search_card.keywords = "[]"

    """Parsing the card type up, which is helpful for creatures.
    Replacing the '—' character since it isn't printable in the console right now"""
    card_types = search_card.c_type.replace("—","-")
    search_card.ctype = card_types
    sub_type = ''
    card_string = check_oracle_text(search_card.oracle_text)
    if "legendary" in card_types.lower(): search_card.is_legendary = 'Yes'
    
    if '-' in card_types:
        card_types = card_types.split('-')
        base_type = card_types[0]
        sub_type = card_types[1]

    """Add to sub tables if they are the appropriate card type """
    if 'Land' in search_card.c_type: Land_handle(card_name,card_string, the_card.color_identity())
    if 'Planeswalker' in search_card.c_type: Planeswalker_handle(search_card.name, search_card.oracle_text, the_card.loyalty())
    if 'Creature' in search_card.c_type: mtg_sql.insert_creature(card_name, sub_type, search_card.cmc, the_card.power(), the_card.toughness(), search_card.keywords)
    if 'sorcery' in search_card.c_type.lower() or 'instant' in search_card.c_type.lower(): Spell_handle(search_card.name,search_card.oracle_text, search_card.c_type)    
        
    oracletext = card_string.lower()  #This is only converted to lower case for checking oracle text for certain keywords
    search_card.has_ETB = ETB_Search(oracletext, search_card.c_type, search_card.keywords)
    search_card.has_target = Target_Search(oracletext, search_card.c_type, search_card.keywords)
    search_card.has_draw = Draw_Search(oracletext)
    ramp = Ramp_Search(oracletext, search_card.c_type)
    if ramp == '-' :
        search_card.has_ramp = ramp
    else:
        search_card.has_ramp = make_list(ramp)
    search_card.has_wipe = Wipe_Search(oracletext, search_card.keywords)    
    activated = Activated_Search(oracletext, search_card.keywords)
    if activated == '-' :
        search_card.has_activated = activated
    else:
        search_card.has_activated = make_list(activated)
    triggered =  Trigger_Search(oracletext, search_card.keywords)
    if triggered == '-' :
        search_card.has_triggered = triggered        
    else:
        search_card.has_triggered = make_list(triggered)    
    
    mtg_sql.insert_card(card_name, search_card.clr_ID, search_card.mana_cost, search_card.cmc, search_card.c_type, search_card.keywords,
                search_card.is_legendary, search_card.has_ETB, search_card.has_ramp, search_card.has_draw, search_card.has_target,
                search_card.has_wipe, search_card.has_activated, search_card.has_triggered, search_card.image_url, search_card.oracle_text)

def Split_Card(the_card):
    """Creates instance of MTG_FaceCards() class and passes it and the details of card being searched to handler
    Returns: nothing
    """
    cardfaces = the_card.card_faces()
    card1 = cardfaces[0]
    card2 = cardfaces[1]
    search_card = MTG_FaceCards(card1['name'], the_card.layout(), card2['name'], the_card.color_identity(), card1['mana_cost'], card2['mana_cost'], mtg_regex.regex_get_cmc(card1['mana_cost']),
                                mtg_regex.regex_get_cmc(card2['mana_cost']), card1['type_line'], card2['type_line'], "", "", 'F:F', "etb1","etb2","ramp1","ramp2","draw1","draw2","target1","target2",
                                "wipe1","wipe2", 'activated1', 'activated2', "triggered1", "triggered2", the_card.image_uris()['normal'], the_card.image_uris()['normal'], check_oracle_text(card1['oracle_text']),
                                check_oracle_text(card2['oracle_text']))

    Handle_Double(the_card, search_card)

def Double_Faced_Card(the_card):
    """Creates instance of MTG_FaceCards() class and passes it and the details of card being searched to Handler, (slightly different than for split cards that have only 1 card image)
    Returns: nothing
    """
    cardfaces = the_card.card_faces()
    card1 = cardfaces[0]
    card2 = cardfaces[1]
    search_card = MTG_FaceCards(card1['name'], the_card.layout(), card2['name'], the_card.color_identity(), card1['mana_cost'], card2['mana_cost'],mtg_regex.regex_get_cmc(card1['mana_cost']),
                                mtg_regex.regex_get_cmc(card2['mana_cost']), card1['type_line'], card2['type_line'], "", "","F:F","etb1","etb2","ramp1","ramp2","draw1","draw2","target1","target2",
                                "wipe1","wipe2", 'activated1', 'activated2',"triggered1", "triggered2", card1['image_uris']['normal'], card2['image_uris']['normal'], check_oracle_text(card1['oracle_text']),
                                check_oracle_text(card2['oracle_text']))
        
    Handle_Double(the_card, search_card)

def Handle_Double(the_card, search_card):
    """ Used for processing cards of the following layouts:
    'adventure' , 'split' ,  'flip'  ,  'transform' , 'modal_dfc' , 'double_faced_token' ,'double_sided'
    Parameters:  'the_card': The scryfall card object
                'search_card': Our instance of MTG_FaceCards() class
    Returns nothing  RUNS insert_face_card() to add to 'Face_Cards' and 'Face_Cards_Condensed' tables
    
    Determines keywords, {'etb', 'ramp', 'draw', 'target', 'wipe', 'activated' , 'triggered'} abilities for split and double-sided cards
    """
    
    search_card.face1_type = search_card.face1_type.replace("—","-")
    search_card.face2_type = search_card.face2_type.replace("—","-")
    cardfaces = the_card.card_faces()
    card1 = cardfaces[0]
    card2 = cardfaces[1]
    
    try:
        keywords = mtg_regex.regex_get_keywords(str(the_card.__dict__.items()))
        # print (card1_keywords)
    except:
        print ("Exception encountered searching keywords for a dual card:", search_card.name)
        keywords = []
    
    if keywords.count("'") >2:
        # print ("Two or more keywords found ", keywords)
        all_kw = keywords.split(",")
        for kw in all_kw:
            """Sorting through the keywords of the_card.__dict__.items() and checking which side ('face')
            of the card it happens on so the lists of keywords for each face is separate """
            # print (kw)
            use_this_str = kw.replace("'","").strip()
            
            if use_this_str.lower() in search_card.face1_oracle_text.lower():
                if len(search_card.face1_keywords) < 2:
                    search_card.face1_keywords= search_card.face1_keywords + kw
                else:
                    search_card.face1_keywords= search_card.face1_keywords + "," + kw    
            if use_this_str.lower() in search_card.face2_oracle_text.lower():
                if len(search_card.face2_keywords) < 2:
                    search_card.face2_keywords= search_card.face2_keywords + kw
                else:
                    search_card.face2_keywords= search_card.face2_keywords + "," + kw    
    else:
        use_this_str = keywords.replace("'","").strip()
        if use_this_str.lower() in search_card.face1_oracle_text.lower(): search_card.face1_keywords = keywords
        if use_this_str.lower() in search_card.face2_oracle_text.lower(): search_card.face2_keywords = keywords    
                    
    if 'Land' in search_card.face1_type: Land_handle(search_card.name,search_card.face1_oracle_text, search_card.clr_ID)
    
    if 'Land' in search_card.face2_type: Land_handle(search_card.flipname,search_card.face2_oracle_text, search_card.clr_ID)
    
    if 'Planeswalker' in search_card.face1_type: Planeswalker_handle(search_card.name, search_card.face1_oracle_text, card1['loyalty'])

    if 'Planeswalker' in search_card.face2_type:
        if 'Planeswalker' in search_card.face1_type:
            ## Both sides of cards are Planeswalker, and side 2 does not have a separate 'loyalty' counters 
            Planeswalker_handle(search_card.flipname, search_card.face2_oracle_text, card1['loyalty'])
        else:
            ## Only side 2 is a Planeswalker, 
            Planeswalker_handle(search_card.flipname, search_card.face2_oracle_text, card2['loyalty'])
   
    if 'Creature' in search_card.face1_type:
        if '-' in search_card.face1_type:
            card_types = search_card.face1_type.split('-')
            base_type = card_types[0]
            sub_type = card_types[1]
        mtg_sql.insert_creature(search_card.name, sub_type, search_card.face1_cmc, card1['power'], card1['toughness'], search_card.face1_keywords)
    
    if 'Creature' in search_card.face2_type:
        if '-' in search_card.face2_type:
            card_types = search_card.face2_type.split('-')
            try:
                base_type = card_types[0]
                sub_type = card_types[1]
            except Exception as e:
                base_type = card_types[0]
                sub_type = base_type
                print (card_types, " Exception error ", e)
        mtg_sql.insert_creature(search_card.flipname, sub_type, search_card.face2_cmc, card2['power'], card2['toughness'], search_card.face2_keywords)
    
    if 'sorcery' in search_card.face1_type.lower() or 'instant' in search_card.face1_type.lower():
        Spell_handle(search_card.name,search_card.face1_oracle_text, search_card.face1_type)
        
    if 'sorcery' in search_card.face2_type.lower() or 'instant' in search_card.face2_type.lower():
        Spell_handle(search_card.flipname,search_card.face2_oracle_text, search_card.face2_type)
    
    ## 'T:F' , 'F:T' fields        
    search_card.is_legendary = Legendary_Search_Faces(search_card.face1_type.lower(), search_card.face2_type.lower())
    
    ## List fields of keywords & mechanics
    search_card.face1_target = Target_Search(search_card.face1_oracle_text.lower(), search_card.face1_type.lower(), search_card.face1_keywords.lower())
    search_card.face2_target = Target_Search(search_card.face2_oracle_text.lower(), search_card.face2_type.lower(), search_card.face2_keywords.lower())
    search_card.face1_draw = Draw_Search(search_card.face1_oracle_text.lower())
    search_card.face2_draw = Draw_Search(search_card.face2_oracle_text.lower())
    search_card.face1_wipe = Wipe_Search(search_card.face1_oracle_text.lower(), search_card.face1_keywords.lower())
    search_card.face2_wipe = Wipe_Search(search_card.face2_oracle_text.lower(), search_card.face2_keywords.lower())
    search_card.face1_ETB = ETB_Search(search_card.face1_oracle_text.lower(), search_card.face1_type.lower(), search_card.face1_keywords.lower())
    search_card.face2_ETB = ETB_Search(search_card.face2_oracle_text.lower(), search_card.face2_type.lower(), search_card.face2_keywords.lower())

    activated1 = Activated_Search(search_card.face1_oracle_text.lower(), search_card.face1_keywords.lower())
    activated2 = Activated_Search(search_card.face2_oracle_text.lower(), search_card.face2_keywords.lower())    
    if activated1 == '-' :
        search_card.face1_activated = activated1
    else:
        search_card.face1_activated = make_list(activated1)        
    if activated2 == '-' :
        search_card.face2_activated = activated2
    else:
        search_card.face2_activated = make_list(activated2)                
    
    triggered1 =Trigger_Search(search_card.face1_oracle_text.lower(), search_card.face1_keywords.lower())
    triggered2 = Trigger_Search(search_card.face2_oracle_text.lower(), search_card.face2_keywords.lower())
    if triggered1 == '-' :
        search_card.face1_triggered = triggered1
    else:
        search_card.face1_triggered = make_list(triggered1)        
    if triggered2 == '-' :
        search_card.face2_triggered = triggered2
    else:
        search_card.face2_triggered = make_list(triggered2)        
        
    ramp1 = Ramp_Search(search_card.face1_oracle_text.lower(), search_card.face1_type.lower())
    ramp2 = Ramp_Search(search_card.face2_oracle_text.lower(), search_card.face2_type.lower())
    if ramp1 == "-":
        search_card.face1_ramp = ramp1
    else:
        search_card.face1_ramp = make_list(ramp1)
    if ramp2 == "-":
        search_card.face2_ramp = ramp2
    else:
        search_card.face2_ramp = make_list(ramp2)

    # name, layout, flipname, clr_ID, mana_cost, cmc, c_type, keywords, is_legend, has_etb, has_ramp, has_draw, has_target, has_wipe, has_activated, has_triggered, image_url, oracle_text
    mtg_sql.insert_face_card(search_card.name, search_card.layout, search_card.flipname, search_card.clr_ID, search_card.face1_cost, search_card.face1_cmc, search_card.face1_type, search_card.face1_keywords,
                     search_card.is_legendary, search_card.face1_ETB, search_card.face1_ramp, search_card.face1_draw, search_card.face1_target, search_card.face1_wipe, search_card.face1_activated,
                     search_card.face1_triggered, search_card.face1_image_url, search_card.face1_oracle_text)
    
    mtg_sql.insert_face_card(search_card.flipname, search_card.layout, search_card.name, search_card.clr_ID, search_card.face2_cost, search_card.face2_cmc, search_card.face2_type, search_card.face2_keywords,
                     search_card.is_legendary[::-1], search_card.face2_ETB, search_card.face2_ramp, search_card.face2_draw, search_card.face2_target, search_card.face2_wipe, search_card.face2_activated,
                     search_card.face2_triggered, search_card.face2_image_url, search_card.face2_oracle_text)
    
convert_layout = {
    'normal' : Single_Sided_Card,
    'meld' : Single_Sided_Card,
    'saga' : Single_Sided_Card,
    'class' : Single_Sided_Card,    
    'leveler' : Single_Sided_Card,
    'host' : Single_Sided_Card,
    'augment' : Single_Sided_Card,
    'emblem' : Single_Sided_Card,    
    'adventure' : Split_Card,
    'split' : Split_Card,
    'flip' : Split_Card,
    'transform' : Double_Faced_Card,
    'modal_dfc' : Double_Faced_Card,
    'double_sided' : Double_Faced_Card,
    'token' : Ignore_Card,
    'double_faced_token' : Ignore_Card,
    'planar' : Ignore_Card,
    'art_series' : Ignore_Card,
    'scheme' : Ignore_Card,
    'vanguard' : Ignore_Card }

"""### CARD LAYOUT HANDLING ###  END """

def scryfall_search_exact(card_name):
    """Queries the scryfall server and gets the relevant card info, and based on the card layout it extracts the data accordingly
    Returns nothing , runs select_case_layout() to handle card data extracting
    """
    time.sleep(.05)
    card_name = card_name.replace("ö","o")
    card_name = card_name.replace("û","u")
    getcard = scrython.cards.Named(exact=card_name)
    # print ()
    # print (card_name)    
    """Flip cards and double sided cards have 2 sets of oracle text
    Scryfall represents multiface cards as a single object with a card_faces array describing the distinct faces.
    RELEVANT CARD FACE (as well as regular cards) OBJECTS:
    image_uris  -  this returns a dictionary containing links for 'small', 'normal', 'large', 'png', 'art_crop', 'border_crop'  .. based on .. which set?
            'small' is ~ 145 x 200     'normal' is ~ 488 x 680 - this fits to screen on my laptop.    'large' is ~ 670 x 930 - also fits to screen

    RAMP  = T/F   - narrow by type  {dork, rock, search for land}
    ETB        = T/F   - narrow by type {fetchramp, draw, lifegain, damage, }
    DRAW    = T/F  - could be a number easy enough
    TARGET    = T/F   - narrow by type {destroy?  damage?   return?}
    ACTIVATED = T/F   - activation cost at the very least!
    TRIGGERED = T/F    - narrow by type?
    BOARD WIPE = T/F   - narrow by type {destroy?  damage?   return?}
    
    .. further ideas  (maybe just check T or F for synergy)
    WHEEL - T/F
    TUTOR - T/F   - narrow by type  {card type, destination?, quantity}
    MILL - T/F  - quantity?  , narrow by type  {target, opponents, self}
    SAC OUTLET - T/F   - cost?   tap?
    BLINK - T/F
    DISCARD - T/F  - quantity?   , narrow by type  {target, opponents, self}
    +1/+1 COUNTERS - T/F  - quantity?   , narrow by type  {target, opponents, self}
    -1/-1 COUNTERS - T/F  - quantity?   , narrow by type  {target, opponents, self}
    ARISTOCRAT (LTB?)- T/F
    GRAVEYARD - T/F    , narrow by type  {cast from?, exile, graveyard hate}
    TOKENS - T/F
    SPELL COPYING  - T/F
    CANTRIP?  - T/F
    CLONE  - target types?
    LIFEGAIN - (AS DONE FOR INSTANTS & SORCERIES)
    DAMAGE  - (AS DONE FOR INSTANTS & SORCERIES)
    TRIBAL - T/F
    !!! COST ABILITIES !!! - this will be helpful for determining the total potential mana cost of a permanent  """
    select_case_layout(getcard.layout(), getcard)   # layout will determine Single sided, split or double faced
    
"""### TEMP METHODS AND MAIN PROGRAM ### """
def quick_test_search(card_name):  # just use this for doing scryfall lookups and printing to the console
    ## This is just used to search and print some card info to the console, 
    getcard = scrython.cards.Named(exact=card_name)
    try:
        card_keywords = mtg_regex.regex_get_keywords(str(getcard.__dict__.items()))
    except:
        card_keywords = "[]"
    print ("Name: ", card_name)
    print ("Layout: ", getcard.layout())
    print ("Colour Identity: ", getcard.color_identity())    
    print ("keywords: ", card_keywords)
    print ("Oracle Text: ", check_oracle_text(getcard.oracle_text()))
    # print (str(getcard.__dict__.items()))
    # print ("image link: ", mtg_regex.regex_get_image(str(getcard.__dict__.items())))
    try:
        print ("image link: ", getcard.image_uris()['normal'])
    except:
        print ("image link: ", mtg_regex.regex_get_image(str(getcard.__dict__.items())))

def lands_to_add():  # REBUILD LANDS TABLE
    scryfall_search_exact ("Island")
    scryfall_search_exact ("Boros Garrison")
    scryfall_search_exact ("Animal Sanctuary")
    scryfall_search_exact ("Arcane Sanctum")
    scryfall_search_exact ("Cabal Stronghold")
    scryfall_search_exact ("Hanweir Battlements")
    scryfall_search_exact ("Access Tunnel")
    scryfall_search_exact ("Akoum Refuge")
    scryfall_search_exact ("Akoum Teeth")
    scryfall_search_exact ("Alpine Meadow")
    scryfall_search_exact ("Ancient Den")
    scryfall_search_exact ("Arctic Treeline")
    scryfall_search_exact ("Ash Barrens")
    scryfall_search_exact ("Axgard Armory")
    scryfall_search_exact ("Azorius Chancery")
    scryfall_search_exact ("Azorius Guildgate")
    scryfall_search_exact ("Bala Ged Sanctuary")
    scryfall_search_exact ("Bant Panorama")
    scryfall_search_exact ("Desert of the Fervent")
    scryfall_search_exact ("Desert of the Glorified")
    scryfall_search_exact ("Desert of the Indomitable")
    scryfall_search_exact ("Desert of the Mindful")
    scryfall_search_exact ("Desert of the True")
    scryfall_search_exact ("Desolate Lighthouse")
    scryfall_search_exact ("Barren Moor")
    scryfall_search_exact ("Battlefield Forge")
    scryfall_search_exact ("Beyeen Coast")
    scryfall_search_exact ("Blackbloom Bog")
    scryfall_search_exact ("Blighted Cataract")
    scryfall_search_exact ("Blighted Fen")
    scryfall_search_exact ("Blighted Gorge")
    scryfall_search_exact ("Blighted Woodland")
    scryfall_search_exact ("Blightstep Pathway")
    scryfall_search_exact ("Searstep Pathway")
    scryfall_search_exact ("Blinkmoth Well")
    scryfall_search_exact ("Bloodfell Caves")
    scryfall_search_exact ("Blossoming Sands")
    scryfall_search_exact ("Bojuka Bog")
    scryfall_search_exact ("Bonders' Enclave")
    scryfall_search_exact ("Boros Guildgate")
    scryfall_search_exact ("Branchloft Pathway")
    scryfall_search_exact ("Boulderloft Pathway")
    scryfall_search_exact ("Brightclimb Pathway")
    scryfall_search_exact ("Grimclimb Pathway")
    scryfall_search_exact ("Buried Ruin")
    scryfall_search_exact ("Canopy Vista")
    scryfall_search_exact ("Castle Ardenvale")
    scryfall_search_exact ("Caves of Koilos")
    scryfall_search_exact ("Cinder Barrens")
    scryfall_search_exact ("Cinder Glade")
    scryfall_search_exact ("Cinder Marsh")
    scryfall_search_exact ("Cloudcrest Lake")
    scryfall_search_exact ("Coastal Tower")
    scryfall_search_exact ("Concealed Courtyard")
    scryfall_search_exact ("Contested Cliffs")
    scryfall_search_exact ("Coral Atoll")
    scryfall_search_exact ("Cradle of the Accursed")
    scryfall_search_exact ("Cragcrown Pathway")
    scryfall_search_exact ("Timbercrown Pathway")
    scryfall_search_exact ("Crosis's Catacombs")
    scryfall_search_exact ("Crumbling Necropolis")
    scryfall_search_exact ("Cryptic Caves")
    scryfall_search_exact ("Darigaaz's Caldera")
    scryfall_search_exact ("Darkbore Pathway")
    scryfall_search_exact ("Slitherbore Pathway")
    scryfall_search_exact ("Darksteel Citadel")
    scryfall_search_exact ("Darkwater Catacombs")
    scryfall_search_exact ("Dimir Aqueduct")
    scryfall_search_exact ("Dimir Guildgate")
    scryfall_search_exact ("Dismal Backwater")
    scryfall_search_exact ("Dragonskull Summit")
    scryfall_search_exact ("Dread Statuary")
    scryfall_search_exact ("Drifting Meadow")
    scryfall_search_exact ("Dromar's Cavern")
    scryfall_search_exact ("Drowned Catacomb")
    scryfall_search_exact ("Drownyard Temple")
    scryfall_search_exact ("Dwarven Mine")
    scryfall_search_exact ("Emergence Zone")
    scryfall_search_exact ("Emeria, Shattered Skyclave")
    scryfall_search_exact ("Encroaching Wastes")
    scryfall_search_exact ("Everglades")
    scryfall_search_exact ("Evolving Wilds")
    scryfall_search_exact ("Faerie Conclave")
    scryfall_search_exact ("Fertile Thicket")
    scryfall_search_exact ("Field of Ruin")
    scryfall_search_exact ("Forest")
    scryfall_search_exact ("Forge of Heroes")
    scryfall_search_exact ("Forgotten Cave")
    scryfall_search_exact ("Forsaken Sanctuary")
    scryfall_search_exact ("Foul Orchard")
    scryfall_search_exact ("Foundry of the Consuls")
    scryfall_search_exact ("Frontier Bivouac")
    scryfall_search_exact ("Gargoyle Castle")
    scryfall_search_exact ("Gates of Istfell")
    scryfall_search_exact ("Geier Reach Sanitarium")
    scryfall_search_exact ("Ghitu Encampment")
    scryfall_search_exact ("Gingerbread Cabin")
    scryfall_search_exact ("Glacial Floodplain")
    scryfall_search_exact ("Gnottvold Slumbermound")
    scryfall_search_exact ("Godless Shrine")
    scryfall_search_exact ("Golgari Guildgate")
    scryfall_search_exact ("Golgari Rot Farm")
    scryfall_search_exact ("Grasping Dunes")
    scryfall_search_exact ("Graypelt Refuge")
    scryfall_search_exact ("Great Furnace")
    scryfall_search_exact ("Great Hall of Starnheim")
    scryfall_search_exact ("Grim Backwoods")
    scryfall_search_exact ("Grixis Panorama")
    scryfall_search_exact ("Grove of the Guardian")
    scryfall_search_exact ("Gruul Guildgate")
    scryfall_search_exact ("Gruul Turf")
    scryfall_search_exact ("Guildless Commons")
    scryfall_search_exact ("Halimar Depths")
    scryfall_search_exact ("Hallowed Fountain")
    scryfall_search_exact ("Haunted Fengraf")
    scryfall_search_exact ("Havenwood Battleground")
    scryfall_search_exact ("High Market")
    scryfall_search_exact ("Highland Forest")
    scryfall_search_exact ("Homeward Path")
    scryfall_search_exact ("Hostile Desert")
    scryfall_search_exact ("Idyllic Grange")
    scryfall_search_exact ("Immersturm Skullcairn")
    scryfall_search_exact ("Inspiring Vantage")
    scryfall_search_exact ("Ipnu Rivulet")
    scryfall_search_exact ("Irrigated Farmland")
    scryfall_search_exact ("Isolated Watchtower")
    scryfall_search_exact ("Izzet Boilerworks")
    scryfall_search_exact ("Izzet Guildgate")
    scryfall_search_exact ("Jund Panorama")
    scryfall_search_exact ("Jungle Basin")
    scryfall_search_exact ("Jungle Hollow")
    scryfall_search_exact ("Jungle Shrine")
    scryfall_search_exact ("Jwar Isle Refuge")
    scryfall_search_exact ("Jwari Ruins")
    scryfall_search_exact ("Kabira Plateau")
    scryfall_search_exact ("Karplusan Forest")
    scryfall_search_exact ("Kazandu Valley")
    scryfall_search_exact ("Kazandu Refuge")
    scryfall_search_exact ("Kazuul's Cliffs")
    scryfall_search_exact ("Kessig Wolf Run")
    scryfall_search_exact ("Khalni Territory")
    scryfall_search_exact ("Khalni Garden")
    scryfall_search_exact ("Kher Keep")
    scryfall_search_exact ("Krosan Verge")
    scryfall_search_exact ("Labyrinth of Skophos")
    scryfall_search_exact ("Adanto, the First Fort")
    scryfall_search_exact ("Llanowar Reborn")
    scryfall_search_exact ("Llanowar Wastes")
    scryfall_search_exact ("Lonely Sandbar")
    scryfall_search_exact ("Lorehold Campus")
    scryfall_search_exact ("Lumbering Falls")
    scryfall_search_exact ("Makindi Mesas")
    scryfall_search_exact ("Malakir Mire")
    scryfall_search_exact ("Memorial to Folly")
    scryfall_search_exact ("Memorial to War")
    scryfall_search_exact ("Mikokoro, Center of the Sea")
    scryfall_search_exact ("Mortuary Mire")
    scryfall_search_exact ("Mossfire Valley")
    scryfall_search_exact ("Mosswort Bridge")
    scryfall_search_exact ("Mountain")
    scryfall_search_exact ("Mountain Valley")
    scryfall_search_exact ("Myriad Landscape")
    scryfall_search_exact ("Mystic Monastery")
    scryfall_search_exact ("Mystic Sanctuary")
    scryfall_search_exact ("Nantuko Monastery")
    scryfall_search_exact ("Naya Panorama")
    scryfall_search_exact ("Necroblossom Snarl")
    scryfall_search_exact ("Needle Spires")
    scryfall_search_exact ("Nephalia Academy")
    scryfall_search_exact ("Nesting Grounds")
    scryfall_search_exact ("New Benalia")
    scryfall_search_exact ("Nomad Outpost")
    scryfall_search_exact ("Opulent Palace")
    scryfall_search_exact ("Orzhov Basilica")
    scryfall_search_exact ("Orzhov Guildgate")
    scryfall_search_exact ("Pelakka Caverns")
    scryfall_search_exact ("Phyrexia's Core")
    scryfall_search_exact ("Pine Barrens")
    scryfall_search_exact ("Plains")
    scryfall_search_exact ("Polluted Mire")
    scryfall_search_exact ("Port of Karfell")
    scryfall_search_exact ("Prairie Stream")
    scryfall_search_exact ("Prismari Campus")
    scryfall_search_exact ("Quandrix Campus")
    scryfall_search_exact ("Quicksand")
    scryfall_search_exact ("Radiant Fountain")
    scryfall_search_exact ("Rakdos Carnarium")
    scryfall_search_exact ("Rakdos Guildgate")
    scryfall_search_exact ("Rejuvenating Springs")
    scryfall_search_exact ("Reliquary Tower")
    scryfall_search_exact ("Remote Isle")
    scryfall_search_exact ("Rimewood Falls")
    scryfall_search_exact ("Rith's Grove")
    scryfall_search_exact ("Riverglide Pathway")
    scryfall_search_exact ("Lavaglide Pathway")
    scryfall_search_exact ("Rix Maadi, Dungeon Palace")
    scryfall_search_exact ("Rocky Tar Pit")
    scryfall_search_exact ("Rogue's Passage")
    scryfall_search_exact ("Rootwater Depths")
    scryfall_search_exact ("Rugged Highlands")
    scryfall_search_exact ("Sanctum of Eternity")
    scryfall_search_exact ("Sandsteppe Citadel")
    scryfall_search_exact ("Sandstone Bridge")
    scryfall_search_exact ("Sapseep Forest")
    scryfall_search_exact ("Savage Lands")
    scryfall_search_exact ("Scavenger Grounds")
    scryfall_search_exact ("Scoured Barrens")
    scryfall_search_exact ("Sea Gate, Reborn")
    scryfall_search_exact ("Seaside Citadel")
    scryfall_search_exact ("Seat of the Synod")
    scryfall_search_exact ("Secluded Steppe")
    scryfall_search_exact ("Sejiri Refuge")
    scryfall_search_exact ("Sejiri Glacier")
    scryfall_search_exact ("Sejiri Steppe")
    scryfall_search_exact ("Selesnya Guildgate")
    scryfall_search_exact ("Selesnya Sanctuary")
    scryfall_search_exact ("Sequestered Stash")
    scryfall_search_exact ("Seraph Sanctuary")
    scryfall_search_exact ("Shadowblood Ridge")
    scryfall_search_exact ("Shimmerdrift Vale")
    scryfall_search_exact ("Shivan Reef")
    scryfall_search_exact ("Silundi Isle")
    scryfall_search_exact ("Silverquill Campus")
    scryfall_search_exact ("Simic Growth Chamber")
    scryfall_search_exact ("Simic Guildgate")
    scryfall_search_exact ("Skyclave Basilica")
    scryfall_search_exact ("Skycloud Expanse")
    scryfall_search_exact ("Slayers' Stronghold")
    scryfall_search_exact ("Slippery Karst")
    scryfall_search_exact ("Smoldering Crater")
    scryfall_search_exact ("Smoldering Marsh")
    scryfall_search_exact ("Smoldering Spires")
    scryfall_search_exact ("Snow-Covered Forest")
    scryfall_search_exact ("Snow-Covered Island")
    scryfall_search_exact ("Snow-Covered Mountain")
    scryfall_search_exact ("Snow-Covered Plains")
    scryfall_search_exact ("Snow-Covered Swamp")
    scryfall_search_exact ("Snowfield Sinkhole")
    scryfall_search_exact ("Soaring Seacliff")
    scryfall_search_exact ("Song-Mad Ruins")
    scryfall_search_exact ("Spikefield Cave")
    scryfall_search_exact ("Spinerock Knoll")
    scryfall_search_exact ("Stalking Stones")
    scryfall_search_exact ("Steam Vents")
    scryfall_search_exact ("Stensia Bloodhall")
    scryfall_search_exact ("Stomping Ground")
    scryfall_search_exact ("Stone Quarry")
    scryfall_search_exact ("Sulfur Falls")
    scryfall_search_exact ("Sulfurous Mire")
    scryfall_search_exact ("Sulfurous Springs")
    scryfall_search_exact ("Sungrass Prairie")
    scryfall_search_exact ("Sunhome, Fortress of the Legion")
    scryfall_search_exact ("Sunken Hollow")
    scryfall_search_exact ("Sunscorched Desert")
    scryfall_search_exact ("Swamp")
    scryfall_search_exact ("Swiftwater Cliffs")
    scryfall_search_exact ("Tainted Field")
    scryfall_search_exact ("Tainted Wood")
    scryfall_search_exact ("Tangled Vale")
    scryfall_search_exact ("Teetering Peaks")
    scryfall_search_exact ("Temple of Abandon")
    scryfall_search_exact ("Temple of Enlightenment")
    scryfall_search_exact ("Temple of Epiphany")
    scryfall_search_exact ("Temple of Malady")
    scryfall_search_exact ("Temple of Mystery")
    scryfall_search_exact ("Temple of Silence")
    scryfall_search_exact ("Temple of the False God")
    scryfall_search_exact ("Temple of Triumph")
    scryfall_search_exact ("Terramorphic Expanse")
    scryfall_search_exact ("The World Tree")
    scryfall_search_exact ("Thespian's Stage")
    scryfall_search_exact ("Thornwood Falls")
    scryfall_search_exact ("Tranquil Cove")
    scryfall_search_exact ("Tranquil Thicket")
    scryfall_search_exact ("Treva's Ruins")
    scryfall_search_exact ("Turntimber Grove")
    scryfall_search_exact ("Umara Skyfalls")
    scryfall_search_exact ("Underground River")
    scryfall_search_exact ("Urborg Volcano")
    scryfall_search_exact ("Urza's Factory")
    scryfall_search_exact ("Valakut Stoneforge")
    scryfall_search_exact ("Spitfire Bastion")
    scryfall_search_exact ("Vastwood Thicket")
    scryfall_search_exact ("Vec Townships")
    scryfall_search_exact ("Vineglimmer Snarl")
    scryfall_search_exact ("Vitu-Ghazi, the City-Tree")
    scryfall_search_exact ("Warped Landscape")
    scryfall_search_exact ("Wastes")
    scryfall_search_exact ("Waterveil Cavern")
    scryfall_search_exact ("Watery Grave")
    scryfall_search_exact ("Wind-Scarred Crag")
    scryfall_search_exact ("Windbrisk Heights")
    scryfall_search_exact ("Witch's Clinic")
    scryfall_search_exact ("Witch's Cottage")
    scryfall_search_exact ("Witherbloom Campus")
    scryfall_search_exact ("Woodland Chasm")
    scryfall_search_exact ("Yavimaya Coast")
    scryfall_search_exact ("Zof Bloodbog")
    scryfall_search_exact ("Crumbling Vestige")
    scryfall_search_exact ("Tournament Grounds")
    scryfall_search_exact ("Endless Sands")
    scryfall_search_exact ("Exotic Orchard")
    scryfall_search_exact ("Survivors' Encampment")
    scryfall_search_exact ("Path of Ancestry")
    scryfall_search_exact ("Haven of the Spirit Dragon")
    scryfall_search_exact ("Gateway Plaza")
    scryfall_search_exact ("Holdout Settlement")
    scryfall_search_exact ("Cave of Temptation")
    scryfall_search_exact ("Aether Hub")
    scryfall_search_exact ("Ally Encampment")
    scryfall_search_exact ("Base Camp")
    scryfall_search_exact ("Opal Palace")
    scryfall_search_exact ("Shimmering Grotto")
    scryfall_search_exact ("Spire of Industry")
    scryfall_search_exact ("Study Hall")
    scryfall_search_exact ("Throne of Makindi")
    scryfall_search_exact ("Transguild Promenade")
    scryfall_search_exact ("Unclaimed Territory")
    scryfall_search_exact ("Unknown Shores")
    scryfall_search_exact ("Interplanar Beacon")
    scryfall_search_exact ("Rupture Spire") 
    scryfall_search_exact ("Command Tower") 
    scryfall_search_exact ("Cavern of Souls") 
    scryfall_search_exact ("Fungal Reaches")
    scryfall_search_exact ("Gavony Township")
    scryfall_search_exact ("Karn's Bastion")
    scryfall_search_exact ("Mage-Ring Network")
    scryfall_search_exact ("Novijen, Heart of Progress")
    scryfall_search_exact ("Oran-Rief, the Vastwood")
    scryfall_search_exact ("Vault of Catlacan")
    scryfall_search_exact ("Dreadship Reef")
    scryfall_search_exact ("Molten Slagheap")
    scryfall_search_exact ("Ruins of Oran-Rief")
    scryfall_search_exact ("Saltcrusted Steppe")
    scryfall_search_exact ("Shrine of the Forsaken Gods")
    scryfall_search_exact ("Calciform Pools")
    scryfall_search_exact ("Surtland Frostpyre")  
    scryfall_search_exact ("Vivid Crag")  
    scryfall_search_exact ("Vivid Creek")  
    scryfall_search_exact ("Vivid Grove")  
    scryfall_search_exact ("War Room") 
    scryfall_search_exact ("Memorial to Genius")  
    scryfall_search_exact ("Ancient Spring")  
    scryfall_search_exact ("Skemfar Elderhall")  
    scryfall_search_exact ("Bretagard Stronghold")  
    scryfall_search_exact ("Storm the Vault") 

def test_sample_group():
    scryfall_search_exact ("Jaya Ballard")
    scryfall_search_exact ("Jiang Yanggu, Wildcrafter")
    scryfall_search_exact ("Nissa, Worldwaker")
    scryfall_search_exact ("Tezzeret the Schemer")
    scryfall_search_exact ("Nissa, Steward of Elements")
    scryfall_search_exact ("Chandra, Novice Pyromancer")
    scryfall_search_exact ("Coveted Jewel")
    scryfall_search_exact ("Alpine Guide")
    scryfall_search_exact ("Centaur Nurturer")
    scryfall_search_exact ("Coiling Oracle")
    scryfall_search_exact ("Elvish Pioneer")
    scryfall_search_exact ("Elvish Rejuvenator")
    scryfall_search_exact ("Farhaven Elf")
    scryfall_search_exact ("Fertilid")
    scryfall_search_exact ("Genesis Hydra")
    scryfall_search_exact ("Knight of the White Orchid")
    scryfall_search_exact ("Lotus Cobra")
    scryfall_search_exact ("Morselhoarder")
    scryfall_search_exact ("Ondu Giant")
    scryfall_search_exact ("Quandrix Cultivator")
    scryfall_search_exact ("Quirion Elves")
    scryfall_search_exact ("Risen Reef")
    scryfall_search_exact ("Rootweaver Druid")
    scryfall_search_exact ("Scholarship Sponsor")
    scryfall_search_exact ("Silverglade Elemental")
    scryfall_search_exact ("Solemn Simulacrum")
    scryfall_search_exact ("Springbloom Druid")
    scryfall_search_exact ("Stoic Farmer")
    scryfall_search_exact ("Trove Warden")
    scryfall_search_exact ("Jaspera Sentinel")
    scryfall_search_exact ("Karametra, God of Harvests")
    scryfall_search_exact ("Knight of the Reliquary")
    scryfall_search_exact ("Krosan Wayfarer")
    scryfall_search_exact ("Incubation Druid")
    scryfall_search_exact ("Kor Cartographer")
    scryfall_search_exact ("Kynaios and Tiro of Meletis")
    scryfall_search_exact ("Alpha Brawl")
    scryfall_search_exact ("The Wanderer")
    scryfall_search_exact ("Davriel, Rogue Shadowmage")
    scryfall_search_exact ("Ashiok, Dream Render")
    scryfall_search_exact ("Saheeli, the Gifted")
    scryfall_search_exact ("Angrath, Captain of Chaos")
    scryfall_search_exact ("Arlinn, Voice of the Pack")
    scryfall_search_exact ("Chandra, Flamecaller")
    scryfall_search_exact ("Chandra, Pyromaster")
    scryfall_search_exact ("Dovin, Hand of Control")
    scryfall_search_exact ("Gideon Jura")
    scryfall_search_exact ("Gideon, Champion of Justice")
    scryfall_search_exact ("Gideon, the Oathsworn")
    scryfall_search_exact ("Huatli, the Sun's Heart")
    scryfall_search_exact ("Jace, Arcane Strategist")
    scryfall_search_exact ("Jaya Ballard")
    scryfall_search_exact ("Jaya, Venerated Firemage")
    scryfall_search_exact ("Jiang Yanggu, Wildcrafter")
    scryfall_search_exact ("Kasmina, Enigma Sage")
    scryfall_search_exact ("Kasmina, Enigmatic Mentor")
    scryfall_search_exact ("Kaya, Bane of the Dead")
    scryfall_search_exact ("Kiora, Behemoth Beckoner")
    scryfall_search_exact ("Nahiri, Storm of Stone")
    scryfall_search_exact ("Narset, Parter of Veils")
    scryfall_search_exact ("Nissa, Worldwaker")
    scryfall_search_exact ("Ob Nixilis, the Hate-Twisted")
    scryfall_search_exact ("Oko, the Trickster")
    scryfall_search_exact ("Saheeli, Sublime Artificer")
    scryfall_search_exact ("Samut, Tyrant Smasher")
    scryfall_search_exact ("Sarkhan the Masterless")
    scryfall_search_exact ("Tibalt, Rakish Instigator")
    scryfall_search_exact ("Ugin, the Ineffable")
    scryfall_search_exact ("Vraska, Swarm's Eminence")
    scryfall_search_exact ("Tamiyo, the Moon Sage")
    scryfall_search_exact ("Teferi, Time Raveler")
    scryfall_search_exact ("Teferi, Timebender")
    scryfall_search_exact ("Teyo, the Shieldmage")
    scryfall_search_exact ("Tezzeret the Schemer")
    scryfall_search_exact ("Cloudcrest Lake")
    scryfall_search_exact ("Coastal Tower")
    scryfall_search_exact ("Concealed Courtyard")
    scryfall_search_exact ("Contested Cliffs")
    scryfall_search_exact ("Coral Atoll")
    scryfall_search_exact ("Cradle of the Accursed")
    scryfall_search_exact ("Cragcrown Pathway")
    scryfall_search_exact ("Timbercrown Pathway")
    scryfall_search_exact ("Crosis's Catacombs")
    scryfall_search_exact ("Crumbling Necropolis")
    scryfall_search_exact ("Cryptic Caves")
    scryfall_search_exact ("Darigaaz's Caldera")
    scryfall_search_exact ("Darkbore Pathway")
    scryfall_search_exact ("Tezzeret, Cruel Machinist")
    scryfall_search_exact ("Nissa, Steward of Elements")
    scryfall_search_exact ("Sorin, Vengeful Bloodlord")
    scryfall_search_exact ("Aminatou, the Fateshifter")
    scryfall_search_exact ("Lord Windgrace")
    scryfall_search_exact ("Estrid, the Masked")
    scryfall_search_exact ("Ajani Unyielding")
    scryfall_search_exact ("Angrath, Minotaur Pirate")
    scryfall_search_exact ("Chandra, Novice Pyromancer")
    scryfall_search_exact ("Daretti, Scrap Savant")
    scryfall_search_exact ("Domri, City Smasher")
    scryfall_search_exact ("Dovin, Architect of Law")
    scryfall_search_exact ("Dovin, Grand Arbiter")
    scryfall_search_exact ("Elspeth, Undaunted Hero")
    scryfall_search_exact ("Garruk, Primal Hunter")
    scryfall_search_exact ("Jace, Architect of Thought")
    scryfall_search_exact ("Malakir Mire")
    scryfall_search_exact ("Memorial to Folly")
    scryfall_search_exact ("Memorial to War")
    scryfall_search_exact ("Mikokoro, Center of the Sea")
    scryfall_search_exact ("Mortuary Mire")
    scryfall_search_exact ("Mossfire Valley")
    scryfall_search_exact ("Mosswort Bridge")
    scryfall_search_exact ("Mountain")
    scryfall_search_exact ("Mountain Valley")
    scryfall_search_exact ("Myriad Landscape")
    scryfall_search_exact ("Mystic Monastery")
    scryfall_search_exact ("Mystic Sanctuary")
    scryfall_search_exact ("Nantuko Monastery")
    scryfall_search_exact ("Naya Panorama")
    scryfall_search_exact ("Necroblossom Snarl")
    scryfall_search_exact ("Needle Spires")
    scryfall_search_exact ("Nephalia Academy")
    scryfall_search_exact ("Nesting Grounds")
    scryfall_search_exact ("New Benalia")
    scryfall_search_exact ("Nomad Outpost")
    scryfall_search_exact ("Opulent Palace")
    scryfall_search_exact ("Orzhov Basilica")
    scryfall_search_exact ("Orzhov Guildgate")
    scryfall_search_exact ("Pelakka Caverns")
    scryfall_search_exact ("Phyrexia's Core")
    scryfall_search_exact ("Pine Barrens")
    scryfall_search_exact ("Plains")
    scryfall_search_exact ("Polluted Mire")
    scryfall_search_exact ("Port of Karfell")
    scryfall_search_exact ("Prairie Stream")
    scryfall_search_exact ("Prismari Campus")
    scryfall_search_exact ("Quandrix Campus")
    scryfall_search_exact ("Quicksand")
    scryfall_search_exact ("Radiant Fountain")
    scryfall_search_exact ("Rakdos Carnarium")
    scryfall_search_exact ("Rakdos Guildgate")
    scryfall_search_exact ("Rejuvenating Springs")
    scryfall_search_exact ("Reliquary Tower")
    scryfall_search_exact ("Remote Isle")
    scryfall_search_exact ("Rimewood Falls")
    scryfall_search_exact ("Rith's Grove")
    scryfall_search_exact ("Riverglide Pathway")
    scryfall_search_exact ("Lavaglide Pathway")
    scryfall_search_exact ("Rix Maadi, Dungeon Palace")
    scryfall_search_exact ("Rocky Tar Pit")
    scryfall_search_exact ("Rogue's Passage")
    scryfall_search_exact ("Rootwater Depths")
    scryfall_search_exact ("Rugged Highlands")
    scryfall_search_exact ("Sanctum of Eternity")
    scryfall_search_exact ("Sandsteppe Citadel")
    scryfall_search_exact ("Sandstone Bridge")
    scryfall_search_exact ("Sapseep Forest")
    scryfall_search_exact ("Savage Lands")
    scryfall_search_exact ("Scavenger Grounds")
    scryfall_search_exact ("Scoured Barrens")
    scryfall_search_exact ("Sea Gate, Reborn")
    scryfall_search_exact ("Seaside Citadel")
    scryfall_search_exact ("Seat of the Synod")
    scryfall_search_exact ("Secluded Steppe")
    scryfall_search_exact ("Sejiri Refuge")
    scryfall_search_exact ("Sejiri Glacier")
    scryfall_search_exact ("Sejiri Steppe")
    scryfall_search_exact ("Selesnya Guildgate")
    scryfall_search_exact ("Selesnya Sanctuary")
    scryfall_search_exact ("Sequestered Stash")
    scryfall_search_exact ("Seraph Sanctuary")
    scryfall_search_exact ("Shadowblood Ridge")
    scryfall_search_exact ("Shimmerdrift Vale")
    scryfall_search_exact ("Liliana, Death Wielder")
    scryfall_search_exact ("Liliana, the Necromancer")
    scryfall_search_exact ("Nahiri, Heir of the Ancients")
    scryfall_search_exact ("Nahiri, the Harbinger")
    scryfall_search_exact ("Nicol Bolas, Planeswalker")
    scryfall_search_exact ("Ob Nixilis Reignited")
    scryfall_search_exact ("Ral Zarek")
    scryfall_search_exact ("Ral, Caller of Storms")
    scryfall_search_exact ("Rowan, Fearless Sparkmage")
    scryfall_search_exact ("Sarkhan, Dragonsoul")
    scryfall_search_exact ("Vivien of the Arkbow")
    scryfall_search_exact ("Vraska, Regal Gorgon")
    scryfall_search_exact ("Vraska, Scheming Gorgon")
    scryfall_search_exact ("Valki, God of Lies")
    scryfall_search_exact ("Tezzeret, Master of the Bridge")
    scryfall_search_exact ("Savage Lands") # Incorrect mana gen
    scryfall_search_exact ("Archfiend of Depravity")
    scryfall_search_exact ("Arcus Acolyte")
    scryfall_search_exact ("Armageddon")
    scryfall_search_exact ("Ashcloud Phoenix")
    scryfall_search_exact ("Ashen Firebeast")
    scryfall_search_exact ("Austere Command")
    scryfall_search_exact ("Back to Nature")
    scryfall_search_exact ("Barrage of Boulders")
    scryfall_search_exact ("Bearer of the Heavens")
    scryfall_search_exact ("Bellowing Aegisaur")
    scryfall_search_exact ("Belltoll Dragon")
    scryfall_search_exact ("Bend or Break")
    scryfall_search_exact ("Blasphemous Act")
    scryfall_search_exact ("Blazing Volley")
    scryfall_search_exact ("Blood on the Snow")
    scryfall_search_exact ("Bloodfire Colossus")
    scryfall_search_exact ("Bloodfire Dwarf")
    scryfall_search_exact ("Bloodfire Kavu")
    scryfall_search_exact ("Bravado")
    scryfall_search_exact ("Breath of Darigaaz")
    scryfall_search_exact ("Brudiclad, Telchor Engineer")
    scryfall_search_exact ("Cabal Paladin")
    scryfall_search_exact ("Calming Verse")
    scryfall_search_exact ("Celestial Kirin")
    scryfall_search_exact ("Chain Reaction")
    scryfall_search_exact ("Chandra, Flamecaller")
    scryfall_search_exact ("Cinder Giant")
    scryfall_search_exact ("Cinderclasm")
    scryfall_search_exact ("Citywide Bust")
    scryfall_search_exact ("Cleanfall")
    scryfall_search_exact ("Cleansing Nova")
    scryfall_search_exact ("Coalhauler Swine")
    scryfall_search_exact ("Conclave's Blessing")
    scryfall_search_exact ("Copperhorn Scout")
    scryfall_search_exact ("Cosmotronic Wave")
    scryfall_search_exact ("Crackling Doom")
    scryfall_search_exact ("Creeping Corrosion")
    scryfall_search_exact ("Crux of Fate")
    scryfall_search_exact ("Cry of the Carnarium")
    scryfall_search_exact ("Crypt Rats")
    scryfall_search_exact ("Damping Sphere")
    scryfall_search_exact ("Dargo, the Shipwrecker")
    scryfall_search_exact ("Deadly Tempest")
    scryfall_search_exact ("Deafening Clarion")
    scryfall_search_exact ("Decree of Annihilation")
    scryfall_search_exact ("Deep Freeze")
    scryfall_search_exact ("Descend upon the Sinful")
    scryfall_search_exact ("Coralhelm Chronicler")
    scryfall_search_exact ("Coveted Jewel")
    scryfall_search_exact ("Crackling Drake")
    scryfall_search_exact ("Dark Intimations")
    scryfall_search_exact ("Demonic Lore")
    scryfall_search_exact ("Disciple of Bolas")
    scryfall_search_exact ("Diviner's Wand")
    scryfall_search_exact ("Dormant Sliver")
    scryfall_search_exact ("Dovin's Acuity")
    scryfall_search_exact ("Dragon Mantle")
    scryfall_search_exact ("Due Respect")
    scryfall_search_exact ("Dusk Legion Zealot")
    scryfall_search_exact ("Eidolon of Blossoms")
    scryfall_search_exact ("Elemental Bond")
    scryfall_search_exact ("Elite Guardmage")
    scryfall_search_exact ("Elvish Visionary")
    scryfall_search_exact ("Era of Innovation")
    scryfall_search_exact ("Ethereal Valkyrie")
    scryfall_search_exact ("Farsight Adept")
    scryfall_search_exact ("Fate Foretold")
    scryfall_search_exact ("Fathom Mage")
    scryfall_search_exact ("Fblthp, the Lost")
    scryfall_search_exact ("Filigree Familiar")
    scryfall_search_exact ("First Day of Class")
    scryfall_search_exact ("Fissure Wizard")
    scryfall_search_exact ("Frog Tongue")
    scryfall_search_exact ("Gadwick, the Wizened")
    scryfall_search_exact ("Garruk's Packleader")
    scryfall_search_exact ("Garruk's Uprising")
    scryfall_search_exact ("Generous Patron")
    scryfall_search_exact ("Alpine Guide")
    scryfall_search_exact ("Centaur Nurturer")
    scryfall_search_exact ("Coiling Oracle")
    scryfall_search_exact ("Dockside Extortionist")
    scryfall_search_exact ("Elvish Pioneer")
    scryfall_search_exact ("Elvish Rejuvenator")
    scryfall_search_exact ("Farhaven Elf")
    scryfall_search_exact ("Fertilid")
    scryfall_search_exact ("Genesis Hydra")
    scryfall_search_exact ("Knight of the White Orchid")
    scryfall_search_exact ("Lotus Cobra")
    scryfall_search_exact ("Morselhoarder")
    scryfall_search_exact ("Ondu Giant")
    scryfall_search_exact ("Prosperous Pirates")
    scryfall_search_exact ("Quandrix Cultivator")
    scryfall_search_exact ("Quirion Elves")
    scryfall_search_exact ("Rapacious Dragon")
    scryfall_search_exact ("Risen Reef")
    scryfall_search_exact ("Rootweaver Druid")
    scryfall_search_exact ("Sailor of Means")
    scryfall_search_exact ("Scholarship Sponsor")
    scryfall_search_exact ("Silverglade Elemental")
    scryfall_search_exact ("Solemn Simulacrum")
    scryfall_search_exact ("Springbloom Druid")
    scryfall_search_exact ("Stoic Farmer")
    scryfall_search_exact ("Trove Warden")
    scryfall_search_exact ("Jaspera Sentinel")
    scryfall_search_exact ("Karametra, God of Harvests")
    scryfall_search_exact ("Knight of the Reliquary")
    scryfall_search_exact ("Krosan Wayfarer")
    scryfall_search_exact ("Ambush Viper")
    scryfall_search_exact ("Incubation Druid")
    scryfall_search_exact ("Jaspera Sentinel")
    scryfall_search_exact ("Karametra, God of Harvests")
    scryfall_search_exact ("Knight of the Reliquary")
    scryfall_search_exact ("Knight of the White Orchid")
    scryfall_search_exact ("Kor Cartographer")
    scryfall_search_exact ("Krosan Wayfarer")
    scryfall_search_exact ("Kynaios and Tiro of Meletis")
    scryfall_search_exact ("Akoum Flameseeker")
    scryfall_search_exact ("Anje Falkenrath")
    scryfall_search_exact ("Anje's Ravager")
    scryfall_search_exact ("Anowon, the Ruin Thief")
    scryfall_search_exact ("Arcanis the Omnipotent")
    scryfall_search_exact ("Adrix and Nev, Twincasters")
    scryfall_search_exact ("Advanced Hoverguard")
    scryfall_search_exact ("Advocate of the Beast")
    scryfall_search_exact ("Aegis Angel")
    scryfall_search_exact ("Aegis Automaton")
    scryfall_search_exact ("Aegis of the Gods")
    scryfall_search_exact ("Aerial Guide")
    scryfall_search_exact ("Aerie Mystics")

def main():
    begin_time = time.time()
    # print (time.localtime(begin_time))    
        ## CLEAR OLD TABLES IF NECESSARY  ##
    # mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Face_Cards_Condensed'")
    # mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Face_Cards'")
    # mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Cards'")
    # mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Cards_Condensed'")
    # mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Grandtable'")
    # mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableCondensed'")
    # mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableSplit'")
    # mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableSplitCondensed'")
    
    # mtg_sql.cur.execute("DROP TABLE IF EXISTS 'All_Decks'")    
    mtg_sql.check_all_tables()  ## SEE IF TABLES EXIST, AND CREATES IF REQUIRED ##
    """ MAIN PROGRAM START"""


    ## Temporary functions, these are mainly for testing 
    # import_inventory()   ## - This should be accessed through the gui instead, so you can specify which file to open, but the option is available
    ###### SEARCH FUNCTIONS
    
    # scryfall_search_exact ("Oath of Lim-Dul")
    # scryfall_search_exact ("Barbarian Class")
    # quick_test_search("Arni Slays the Troll")

    # delete_all_zdecktables()    
    # import_all_decks()
    # create_all_decks()
    # test_sample_group()
    
    ### Build the GUI (tkinter) window 
    d = gui_class.MTG_GUI(gui_class.root)
    d.fill_decklist()
    d.new_deck()
    d.set_event_bindings()
    gui_class.root.mainloop()

    # save changes to the SQL tables
    mtg_sql.db.commit()
    mtg_sql.db.close()
    """ MAIN PROGRAM END"""
    end_time = time.time()
    run_time = end_time - begin_time
    remaining_time = run_time
    print_runtime = ""
    if remaining_time > 3600:
        hours_time = remaining_time / 3600
        remaining_time = remaining_time % 3600
        print_runtime = print_runtime + str(int(hours_time)) + " hours "
    if remaining_time > 60:
        mins_time = remaining_time / 60
        remaining_time = remaining_time % 60
        print_runtime = print_runtime + str(int(mins_time)) + " min " + str(round(remaining_time,1)) + " sec"
    else:
        print_runtime = print_runtime + str(round(remaining_time,1)) + " sec"
    print ("Runtime :", print_runtime)
    # print (time.localtime(end_time))

if __name__ == '__main__': main()