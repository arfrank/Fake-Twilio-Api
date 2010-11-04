def required(required_list,request):
	for item in required_list:
		if request.get(item,None) is None:
			return False
	return True