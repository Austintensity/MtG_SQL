"""Notes:

Entire inventory cardlist is saved as comma separated values   (approximately 7300 entries)
Name, Type, Cost, Image URL

Type example:  'Creature - Human Shaman'
Cost format examples:  '{3}{W}{U}{B}{R}{G}'
					   '{2}{R}{R}{G}' 
					   '{2W}{2U}{2B}{2R}{2G}'   #  Reaper King - actual CMC varies from 5 to 10   , rare cases where inside the brackets will contain letter and number
					   '{3}{RG}'   # something like Rosheen Meanderer - where it uses Gruul as a mana type .. that's gonna add some complexity to determining CMC
Image Url example:  'https://deckbox.org/system/images/mtg/cards/96953.jpg'


Cost format will need to be converted to both Colour Code , and also CMC

Convert '{2W}{2U}{2B}{2R}{2G}' to WUBRG ,  CMC:10
'{3}{W}{U}{B}{R}{G}'  to WUBRG, CMC:8
'{3}{RG}' to ..RG, CMC: 4 (.. not 5)


"""


# string.replace(old, new, count)
# Parameters :
# 
# old : old substring you want to replace.
# new : new substring which would replace the old substring.
# count : the number of times you want to replace the old substring with the new substring. (Optional)

convert_this = '{1}{W}{W}'
# clr_id = ""
# if 'W' in convert_this:
# 	clr_id = clr_id + 'W'
# if 'U' in convert_this:
# 	clr_id = clr_id + 'U'
# if 'B' in convert_this:
# 	clr_id = clr_id + 'B'
# if 'R' in convert_this:
# 	clr_id = clr_id + 'R'
# if 'G' in convert_this:
# 	clr_id = clr_id + 'G'
# print (convert_this + " has the colour code: " + clr_id)

reduced_convert = convert_this.replace('}', ' ')
reduce_more = reduced_convert.replace('{', '')
split_cost = reduce_more.split(' ')
print (split_cost)
split_cost.pop()
print(split_cost)
print (str(split_cost) + ' has length ' + str(len(split_cost)))
start_cost = 0
for costs in split_cost:

	if costs.isalpha():
		print('alphabetical')
		# removed_wu = costs.replace('WU','1')
		# removed_wb = removed_wu.replace('WB','1')
		# removed_wr = removed_wb.replace('WR','1')
		# removed_wg = removed_wr.replace('WG','1')
		# removed_ub = removed_wg.replace('UB','1')
		# removed_ur = removed_ub.replace('UR','1')
		# removed_ug = removed_ur.replace('UG','1')
		# removed_br = removed_ug.replace('BR','1')
		# removed_bg = removed_br.replace('BG','1')
		# removed_rg = removed_bg.replace('RG','1')
		# removed_w = removed_rg.replace('W','1')
		# removed_u = removed_w.replace('U','1')
		# removed_b = removed_u.replace('B','1')
		# removed_r = removed_b.replace('R','1')
		# removed_g = removed_r.replace('G','1')
		
		try:
			start_cost = int(start_cost) + 1 #int(removed_g)
			print (start_cost)
		except:
			pass
	elif costs.isnumeric():
		print('numeric')
		try:
			start_cost = int(start_cost) + int(costs)
		except:
			pass
	elif costs.isalnum():
		print('alphanumeric')
		try:
			start_cost = int(start_cost) + 1
		except:
			pass

# print (str(len(split_cost)) + " items in the string")
print (str(start_cost) + " is the (minimum) total CMC")
