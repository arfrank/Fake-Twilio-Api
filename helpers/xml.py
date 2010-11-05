"""
Not ideal, but for now, roll my own XML creation.

Will definitely replace at first opportunity

Supports only nested dictionaries right now.
"""
def to_xml(dictionary):
	string = ''
	for item in dictionary:
		if type(dictionary[item]) is dict:
			string += "<"+item+">"+to_xml(dictionary[item])+"</"+item+">"
		else:
			string +='<'+item+'>'+str(dictionary[item])+"</"+item+">"
	return string	