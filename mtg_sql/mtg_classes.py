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


"""MTG_Cards and MTG_FaceCards are the only ones that are getting any use so far.. the others are placeholders for now """

class MTG_Cards:
    def __init__(self, name, layout, clr_ID, mana_cost, cmc, c_type, keywords, is_legendary, has_ETB, has_ramp, has_draw, has_target, has_wipe, has_activated, has_triggered, image_url, oracle_text):
        self.name = name
        self.layout = layout
        self.clr_ID = clr_ID
        self.mana_cost = mana_cost
        self.cmc = cmc
        self.c_type = c_type
        self.keywords = keywords
        self.is_legendary = is_legendary
        self.has_ETB = has_ETB
        self.has_ramp = has_ramp
        self.has_draw = has_draw
        self.has_target = has_target
        self.has_wipe = has_wipe
        self.has_activated = has_activated
        self.has_triggered = has_triggered
        self.image_url = image_url
        self.oracle_text = oracle_text

class MTG_FaceCards:
    def __init__(self, name, layout, flipname, clr_ID, face1_cost, face2_cost, face1_cmc, face2_cmc, face1_type, face2_type, face1_keywords,
                 face2_keywords, is_legendary, face1_ETB, face2_ETB, face1_ramp, face2_ramp, face1_draw, face2_draw, face1_target, face2_target,
                 face1_wipe, face2_wipe, face1_activated, face2_activated, face1_triggered, face2_triggered, face1_image_url, face2_image_url, face1_oracle_text, face2_oracle_text):
        self.name = name
        self.layout = layout
        self.flipname = flipname
        self.clr_ID = clr_ID  # this should represent the combined colours of both sides for double faced cards
        self.face1_cost = face1_cost  ## ex: {W}{U}{2}
        self.face2_cost = face2_cost
        self.face1_cmc = face1_cmc  # ex: 4   (based on  {W}{U}{2})
        self.face2_cmc = face2_cmc
        self.face1_type = face1_type
        self.face2_type = face2_type
        self.face1_keywords = face1_keywords
        self.face2_keywords = face2_keywords
        self.is_legendary = is_legendary   ## format  T:T  for 'TRUE' on both faces
        self.face1_ETB = face1_ETB
        self.face2_ETB = face2_ETB
        self.face1_ramp = face1_ramp
        self.face2_ramp = face2_ramp
        self.face1_draw = face1_draw
        self.face2_draw = face2_draw
        self.face1_target = face1_target
        self.face2_target = face2_target
        self.face1_wipe = face1_wipe
        self.face2_wipe = face2_wipe
        self.face1_activated = face1_activated
        self.face2_activated = face2_activated
        self.face1_triggered = face1_triggered
        self.face2_triggered = face2_triggered
        self.face1_image_url = face1_image_url   ## ex: https://c1.scryfall.com/file/scryfall-cards/normal/front/0/0/0005c844-787c-4f0c-8d25-85cec151642b.jpg?1592710235
        self.face2_image_url = face2_image_url
        self.face1_oracle_text = face1_oracle_text
        self.face2_oracle_text = face2_oracle_text

class MTG_Colours:
    def __init__(self, c_id, guild):
        self.id = c_id
        self.guild = guild

    def Get_Clr_ID(manastring):
        clr_id = ""
        if 'W' in manastring:
            clr_id = clr_id + 'W'
        if 'U' in manastring:
            clr_id = clr_id + 'U'
        if 'B' in manastring:
            clr_id = clr_id + 'B'
        if 'R' in manastring:
            clr_id = clr_id + 'R'
        if 'G' in manastring:
            clr_id = clr_id + 'G'
        # print (clr_id)
        return (clr_id)
# 
# class MTG_Decks:
#     def __init__(self, D_id, Name, Clr_ID, Commander, Num_Clrs, Tier, Ramp, Card_Draw, Target_Removal, Board_Wipe):
#         self.id = D_id
#         self.Clr_ID = Clr.ID
#         self.Name = Name
#         self.Commander = Commander
#         self.Num_Clrs = Num_Clrs   # Although in almost every case, this will simply equal len(Clr_ID)
#         self.Tier = Tier
#         self.Ramp = Ramp
#         self.Card_Draw = Card_Draw
#         self.Target_Removal = Target_Removal
#         self.Board_Wipe = Board_Wipe

# class MTG_Creatures:
#     def __init__(self, name, creature_type, power, toughness):
#         self.name = name
#         self.creature_type = creature_type # ie Tribe
#         self.power = power
#         self.toughness = toughness
# 
# # Instants and Sorceries
# class MTG_Spell:
#     "Could optionally go into more sub categories like Mill, Discard, Graveyard mechanics etc.."
#     def __init__(self, name, spell_type, hashealing, hasdamage):
#         self.name = name
#         self.spell_type = spell_type
#         self.hashealing = hashealing
#         self.hasdamage = hasdamage
# 
# class MTG_Planeswalkers:
#     def __init__(self, name, loyalty, is_passive, boost_ability, cost_ability, ultimate):
#         self.name = name
#         self.loyalty = loyalty
#         self.is_passive = is_passive
#         self.boost_ability = boost_ability
#         self.cost_ability = cost_ability
#         self.ultimate = ultimate
# 
# class MTG_Land:
#     def __init__(self, name, mana, clr_type, has_additional):
#         self.name = name
#         self.mana = mana
#         self.clr_type = clr_type
#         self.has_additional = has_additional # some land cards have more than 1 tap ability to produce different mana
# 
# # playerlist = ['Player 1', 'Player 2', 'Player 3', 'Player 4']
# class MTG_GameStats:
#     def __init__(self, ID, playerlist, winner, first_out, turn_number, notes):
#         self.ID = ID
#         self.playerlist = playerlist
#         self.winner = winner
#         self.first_out = first_out
#         self.turn_number
#         self.notes = notes

#############################
###  DISCONTINUED
###########################

# # class MTG_Art_Ench:
# #     """the MTG_Cards class is already tracking whether this card is for Ramp, Draw, removal,etc purposes, description
# #     for the time being will just be brief notes on what the card does"""
# #     def __init__(self, name, spell_type, activated_ability, triggered_ability, is_passive, description):
# #         self.name = name
# #         self.spell_type = spell_type
# #         self.activated_ability = activated_ability
# #         self.triggered_ability = triggered_ability
# #         self.is_passive = is_passive
# #         self.description = description
