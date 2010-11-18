import re
import logging

from models import incoming_phone_numbers, outgoing_caller_ids

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
