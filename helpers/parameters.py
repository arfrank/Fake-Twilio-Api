import urlparse
import re
import logging

from models import incoming_phone_numbers, outgoing_caller_ids
def arg_or_request(arg_value,request, arg_name, default = None):
	return arg_value if ((arg_value is not None and arg_value != '') or request is None) else request.get(arg_name, default)
#Parses the given phone number, and then makes sure that it can be put into a valid twilio format.
#Returns the twilio formatted phone_number and whether or not it went well, Valid or not

def parse_phone_number(phone_number):
	#TAKEN FROM DIVE INTO PYTHON
	# http://diveintopython.org/
	phonePattern = re.compile(r'''
	    (\+1)*          # optional +1 capture don't match beginning of string, number can start anywhere
	    (\d{3})     # area code is 3 digits (e.g. '800')
	    \D*         # optional separator is any number of non-digits
	    (\d{3})     # trunk is 3 digits (e.g. '555')
	    \D*         # optional separator
	    (\d{4})     # rest of number is 4 digits (e.g. '1212')
	    \D*         # optional separator
	    (\d*)       # extension is optional and can be any number of digits
	    $           # end of string
	    ''', re.VERBOSE)
	try:
		phoneGroups = phonePattern.search(phone_number).groups()
		pn = '+1'+str(phoneGroups[1])+str(phoneGroups[2])+str(phoneGroups[3])
	except Exception, e:
		#logging.info('having trouble parsing phone number: '+phone_number)
		return phone_number, False, ()
	else:
		#logging.info('successful parsing phone number: '+phone_number)
		return pn, True, phoneGroups
	#should actually parse # and check for truth

def valid_to_phone_number(phone_number,required = False, SMS = False):
	TOLL_FREE_PREFIXES = ['800','888','877','866','855','844','833','822','880','881','882','883','884','885','886','887','889']
	OTHER_PREFIXES = ['900','976','411','911']
	LOCAL_NUMBERS = ['5551212']
	if (phone_number is None or phone_number == '') and required:
		if SMS:
			return False, 21604, 'http://www.twilio.com/docs/errors/21604'
		else:
			return False, 13224, 'http://www.twilio.com/docs/errors/13224'	
	else:
		number_parsed, Valid, phoneGroups = parse_phone_number(phone_number)
		if Valid:
			if str(phoneGroups[1]) in OTHER_PREFIXES or str(phoneGroups[2])+str(phoneGroups[3]) in LOCAL_NUMBERS:
				if SMS:
					return False, 14101, 'http://www.twilio.com/docs/errors/14101'
				else:
					#Dial has invalid to number based upon prefixes/local #
					return False, 13224, 'http://www.twilio.com/docs/errors/13224'
			elif SMS == True and str(phoneGroups[1]) in TOLL_FREE_PREFIXES:
				return False, 14101,'14101'
			else:
				return True, 0, ''
		else:
			if required:
				if SMS:
					return False, 14101, 'http://www.twilio.com/docs/errors/14101'
				else:
					return False, 13224, 'http://www.twilio.com/docs/errors/13224'
			else:
				return True, 21401, 'http://www.twilio.com/docs/errors/21401'

def valid_from_phone_number(phone_number, required = False, Direction = 'outbound-api', SMS = False):
	#logging.info('Trying to send a from message for SMS:' +str(SMS)+' '+str(phone_number))
	if (phone_number is None or phone_number == '') and required:
		return False, 21603, 'http://www.twilio.com/docs/errors/21603'
	else:
#		logging.info('from phone number not none, and required')
		number_parsed, Valid, phoneGroups = parse_phone_number(phone_number)
		if Valid:
			#logging.info('valid from phone number, but is it outgoing')
			#logging.info('Direction is: '+str(Direction))
			if Direction in ['outbound-call','outbound-api','outbound-reply']:
				#logging.info('outgoing direction from phone number')
				#need to check numbers
				#first check if we have that phone number as an incoming phone number
				PN = incoming_phone_numbers.Incoming_Phone_Number.all().filter('PhoneNumber =',number_parsed).get()
				if PN is None:
					#logging.info('Not an incoming phone number to be used')
					#logging.info('no incoming phone number')
					if SMS:
						return False, 14108, 'http://www.twilio.com/docs/error/14108'
					else:
						PN = outgoing_caller_ids.Outgoing_Caller_Id.all().filter('PhoneNumber =',number_parsed).get()
						if PN is None:
							#logging.info('could not find an outgoing number')
							return False, 21212, 'http://www.twilio.com/docs/errors/21212'
						else:
							return True, 0, ''
				else:
					return True, 0, ''
			else:
				return True, 0, ''
		else:
			#logging.info('not  a valid from phone number')
			return False, 21401, 'http://www.twilio.com/docs/errors/21401'

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