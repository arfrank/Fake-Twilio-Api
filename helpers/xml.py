"""
Not ideal, but for now, roll my own XML creation.

Will definitely replace at first opportunity

Supports only nested dictionaries right now.
"""
def to_xml(dictionary):
	string = ""
	for item in dictionary:
		if type(dictionary[item]) is dict:
			string += "<"+item+">"+to_xml(dictionary[item])+"</"+item+">"
		elif type(dictionary[item]) is list:
			for element in dictionary[item]:
				string+="<"+item+">"+to_xml(element)+"</"+item+">"
		else:
			string +="<"+item+">"+str(dictionary[item])+"</"+item+">"
	return string
	
# depreciated
def add_nodes(dictionary,resource_name):
	return {
			"TwilioResponse":
				{
				str(resource_name) : dictionary
				}
			}