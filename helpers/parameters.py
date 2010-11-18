import urlparse
import re
import logging

from models import incoming_phone_numbers, outgoing_caller_ids
def arg_or_request(arg_value,request, arg_name, default = None):
	return arg_value if ((arg_value is not None and arg_value != '') or request is None) else request.get(arg_name, default)
#Parses the given phone number, and then makes sure that it can be put into a valid twilio format.
#Returns the twilio formatted phone_number and whether or not it went well, Valid or not


def valid_body(body, required=True):
	if (body is None or body == '') and required:
		return False, 14103, 'http://www.twilio.com/docs/errors/14103'
	else:
		if body is not None and  len(body) > 160:
			return False, 21605, 'http://www.twilio.com/docs/errors/21605'
		else:
			return True, 0, ''

def required(required_list,request):
	Valid = True
	for item in required_list:
		if request.get(item,None) is None:
			Valid = False
	if Valid:
		return Valid, 0, ''
	else:
		return Valid, 666, 'Need a parameter'
	
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

#Does a basic check of url validity for netlocation and scheme being used
def check_url(URL):
	if URL is not None and URL != '':
		parse_result = urlparse.urlparse(URL.lower())
		return (parse_result.scheme == 'http' and parse_result.netloc != '')
	else:
		return True

# Checks for the normal callback url to make sure they are valid
def standard_urls(ArgValue):
	if ArgValue is not None:
	  	if check_url(ArgValue):
			return True, 0, ''
		else:
			return False, 21502, 'http://www.twilio.com/docs/errors/21502'
	else:
		return True, 0, ''

#What should this pass back?
#Passed,Twilio error code, Twilio error message
#Checks fallback urls for validity, normal callback being created (cant have fallback without normal callback)
def fallback_urls(fallback_arg_value, standard_arg_value, StandardArgName, Instance, method = 'Voice'):
	# need to check that its a valid url,
	if fallback_arg_value != '': #if not passed, then returns ''
		if check_url(fallback_arg_value):
			# need to check that a standard url is passed, or set already
			if standard_arg_value != '' or getattr(Instance,StandardArgName) is not None:
				return True, 0, ''
			else:
				#Hack to check for sms fallback missing or not.
				if method == 'SMS':
					return False, 21406,'http://www.twilio.com/docs/errors/21406'
				elif method == 'Voice':
					return False, 21405,'http://www.twilio.com/docs/errors/21405'
				
		else:
			return False, 21502, 'http://www.twilio.com/docs/errors/21502'
	else:
		return True, 0, ''

def friendlyname_length(parameter,min_length=1, max_length = 64):
	if min_length <= len(parameter) <= max_length:
		return True, 0 , ''
	else:
		return False, 20002, 'http://www.twilio.com/docs/errors/20002'

#NEED TO TWILIOIZE THIS
#need to better twilioize this
def allowed_boolean(parameter):
	TRUE_BOOLS = [True,1,'true','True','TRUE']
	FALSE_BOOLS = [False,0,'false','False','FALSE']
	if parameter in TRUE_BOOLS or parameter in FALSE_BOOLS:
		return True, 0, ''
	else:
		return False, 0, 'Invalid boolean parameter'