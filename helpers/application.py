
def required(required_list, request):
	val = True
	for item in required_list:
		if request.get(item,None) is None or request.get(item,None) == '':
			val = False
	return val
