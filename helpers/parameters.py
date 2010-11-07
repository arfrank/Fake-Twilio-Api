def required(required_list,request):
	for item in required_list:
		if request.get(item,None) is None:
			return False
	return True
	
def methods(parameter_name,request, default = 'POST'):
	#returns method type in either get or post, defaults to default post, but that can be changed.
	METHOD_TYPES = ['GET','POST']
	return request.get(parameter_name).upper() if (request.get(parameter_name,None) is not None and request.get(parameter_name).upper() in METHOD_TYPES) else default

#Boolean of the above
def allowed_methods(parameter,METHOD_TYPES = ['GET','POST']):
	return parameter.upper() in METHOD_TYPES
	
def standard_urls():
	pass

def fallback_urls(StandardUrl,FallbackUrl,Instance):
	pass
	
def allowed_boolean(parameter):
	TRUE_BOOLS = [True,1,'true','True','TRUE']
	FALSE_BOOLS = [False,0,'false','False','FALSE']
	if parameter in TRUE_BOOLS or parameter in FALSE_BOOLS:
		return True
	else:
		return False