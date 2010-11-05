def required(required_list,request):
	for item in required_list:
		if request.get(item,None) is None:
			return False
	return True
	
def methods(parameter,request, default = 'POST'):
	#returns method type in either get or post, defaults to default post, but that can be changed.
	METHOD_TYPES = ['GET','POST']
	return request.get(parameter).upper() if (request.get(parameter,None) is not None and request.get(parameter).upper() in METHOD_TYPES) else default