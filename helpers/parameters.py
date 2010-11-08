import urlparse

def required(required_list,request):
	Valid = True
	for item in required_list:
		if request.get(item,None) is None:
			Valid = False
	if Valid:
		return Valid, 0, ''
	else:
		return Valid, 
	
#depreciated, moving to more individualized helpers
def methods(parameter_name, request, default = 'POST'):
	#returns method type in either get or post, defaults to default post, but that can be changed.
	METHOD_TYPES = ['GET','POST']
	return request.get(parameter_name).upper() if (request.get(parameter_name,None) is not None and request.get(parameter_name).upper() in METHOD_TYPES) else default

#Boolean of the above
def phone_allowed_methods(parameter,METHOD_TYPES = ['GET','POST']):
	if parameter is not None:
		if parameter.upper() in METHOD_TYPES:
			return True, 0, ''
		else:
			return False, 21403, 'http://www.twilio.com/docs/errors/21403'
	else:
		return False, 21403, 'http://www.twilio.com/docs/errors/21403'

def sms_allowed_methods(parameter,METHOD_TYPES = ['GET','POST']):
	if parameter is not None:
		if parameter.upper() in METHOD_TYPES:
			return True, 0, ''
		else:
			return False, 14104, 'http://www.twilio.com/docs/errors/14104'
	else:
		#this is not right, think its actually 21403
		return False, 14104, 'http://www.twilio.com/docs/errors/14104'

def standard_urls(request,StandardArgName):
	if check_url(request.get(StandardArgName,'')):
		return True, 0, ''
	else:
		return False, 21502, 'http://www.twilio.com/docs/errors/21502'
#What should this pass back?
#Passed,Twilio error code, Twilio error message
def fallback_urls(request, FallbackArgName, StandardArgName, Instance, method = 'Voice'):
	# need to check that its a valid url,
	if check_url(request.get('FallbackArgName')):
		# need to check that a standard url is passed, or set already
		if request.get(StandardArgName,None) is not None or getattr(Instance,StandardArgName) is not None:
			return True, 0, ''
		else:
			#Hack to check for sms fallback missing or not.
			if method == 'SMS':
				return False, 21406,'http://www.twilio.com/docs/errors/21406'
			elif method == 'Voice':
				return False, 21405,'http://www.twilio.com/docs/errors/21405'
				
	else:
		return False, 21502, 'http://www.twilio.com/docs/errors/21502'

def check_url(URL):
	parse_result = urlparse.urlparse(URL.lower())
	return (parse_result.scheme == 'http' and parse_result.netloc != '')

def FriendlyName_length(parameter,min_length=1, max_length = 64):
	if min_length <= len(parameter) <= max_length:
		return True, 0 , ''
	else:
		return False, 20002, 'http://www.twilio.com/docs/errors/20002'
#NEED TO TWILIOIZE THIS
def allowed_boolean(parameter):
	TRUE_BOOLS = [True,1,'true','True','TRUE']
	FALSE_BOOLS = [False,0,'false','False','FALSE']
	if parameter in TRUE_BOOLS or parameter in FALSE_BOOLS:
		return True, 0, ''
	else:
		return False, 0, 'Invalid boolean parameter'