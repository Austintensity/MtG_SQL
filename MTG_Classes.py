#  2021  Paul Austin
#  For the purposes of this project, it is assumed that no two (different) Magic the Gathering cards exist that have
#  the same name, even though that might not necessarily be the case..

# MTG_COLOURS    ' is colour_id the only potential foreign key..??
# MTG_DECKS
# MTG_CARDS
# MTG_LAND
# MTG_CREATURES
# MTG_SPELL
# MTG_ART_ENCH
# MTG_PLANESWALKER
# MTG_GAMESTATS

class MTG_Colours:  
	def __init__(self, c_id, guild):
		self.id = c_id
		self.guild = guild
		
	def Get_CMC(manastring):
		pass

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
		print (clr_id)
		return (clr_id)
	
class MTG_Decks:
	def __init__(self, D_id, Name, Clr_ID, Commander, Num_Clrs, Tier, Ramp, Card_Draw, Target_Removal, Board_Wipe):
		self.id = D_id
		self.Clr_ID = Clr.ID
		self.Name = Name
		self.Commander = Commander,
		self.Num_Clrs = Num_Clrs   # Although in almost every case, this will simply equal len(Clr_ID)
		self.Tier = Tier
		self.Ramp = Ramp
		self.Card_Draw = Card_Draw
		self.Target_Removal = Target_Removal
		self.Board_Wipe = Board_Wipe
	
class MTG_Cards:
	def __init__(self, name, clr_ID, cost, c_type, is_permanent, is_legendary, has_ETB, has_ramp, has_draw, has_target, has_wipe, has_activated, has_triggered, is_passive):
		self.name = name
		self.clr_ID = clr_ID,
		self.cost = cost
		self.c_type = c_type
		self.is_permanent = is_permanent
		self.is_legendary = is_legendary
		self.has_ETB = has_ETB
		self.has_ramp = has_ramp
		self.has_draw = has_draw
		self.has_target = has_target
		self.has_wipe = has_wipe
		self.has_activated = has_activated
		self.has_triggered = has_triggered
		self.is_passive = is_passive
		

class MTG_Creatures:
	def __init__(self, name, creature_type, power, toughness):
		self.name = name
		self.creature_type = creature_type # ie Tribe
		self.power = power
		self.toughness = toughness

# Instants and Sorceries	
class MTG_Spell:   
	"Could optionally go into more sub categories like Mill, Discard, Graveyard mechanics etc.."
	def __init__(self, name, spell_type, hashealing, hasdamage):
		self.name = name
		self.spell_type = spell_type
		self.hashealing = hashealing
		self.hasdamage = hasdamage

class MTG_Art_Ench:
	"""the MTG_Cards class is already tracking whether this card is for Ramp, Draw, removal,etc purposes, description
	for the time being will just be brief notes on what the card does"""
	def __init__(self, name, spell_type, activated_ability, triggered_ability, is_passive, description):
		self.name = name
		self.spell_type = spell_type
		self.activated_ability = activated_ability
		self.triggered_ability = triggered_ability
		self.is_passive = is_passive
		self.description = description
		
class MTG_Planeswalkers:
	def __init__(self, name, loyalty, is_passive, boost_ability, cost_ability, ultimate):
		self.name = name
		self.loyalty = loyalty
		self.is_passive = is_passive
		self.boost_ability = boost_ability
		self.cost_ability = cost_ability
		self.ultimate = ultimate
	
class MTG_Land:
	def __init__(self, name, mana, clr_type, has_additional):
		self.name = name
		self.mana = mana
		self.clr_type = clr_type
		self.has_additional = has_additional # some land cards have more than 1 tap ability to produce different mana

# playerlist = ['Player 1', 'Player 2', 'Player 3', 'Player 4']
class MTG_GameStats:
	def __init__(self, ID, playerlist, winner, first_out, turn_number, notes):
		self.ID = ID
		self.playerlist = playerlist
		self.winner = winner
		self.first_out = first_out
		self.turn_number
		self.notes = notes

