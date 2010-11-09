from google.appengine.ext import db
from models import base
from random import random
from hashlib import sha256

from helpers import parameters

import datetime

class Message(base.CommonModel):
	To = db.StringProperty()
	From = db.StringProperty()
	Body = db.StringProperty()
	DateSent = db.DateTimeProperty()
	AccountSid = db.StringProperty()
	Sid = db.StringProperty()
	Status = db.StringProperty()
	Direction = db.StringProperty()
	Price = db.FloatProperty()
	StatusCallback = db.StringProperty()

	@classmethod
	def new(cls, request, AccountSid, **kwargs):
		property_dictionary = {}
		Valid = True
		arg_length = len(kwargs)
		for keyword in kwargs:
			if hasattr(cls,keyword) and kwargs[keyword] is not None:
				Valid, TwilioCode, TwilioMsg = cls().validate( request, keyword, kwargs[keyword] )
				if not Valid:
					break
				else:
					property_dictionary[keyword] = cls().sanitize(request, keyword, kwargs[keyword])
		if Valid:
			Sid = 'SM'+sha256(str(random())).hexdigest()
			return cls(
						Sid = Sid,
						AccountSid = AccountSid,
						**property_dictionary
					), True, 0, ''
		else:
			return '', False, TwilioCode, TwilioMsg
	
	@classmethod
	def new_Sid(self):
		return 'SM'+sha256(str(random())).hexdigest()

	def send(self):
		self.Status = 'sent'
		self.Price = 0.03
		self.DateSent = datetime.datetime.now()
		self.put()
	
	def error(self):
		self.Status = 'failed'
		self.Price = 0.00
		self.put()
		
	def validate(self, request, arg_name,arg_value):
		validators = {
			'To' : parameters.valid_to_phone_number(request.get('To',None),required=True),
			'From' : parameters.valid_from_phone_number(request.get('From',None),required=True),
			'Body' : parameters.valid_body(request.get('Body',None),required=True),
			'StatusCallback' : parameters.standard_urls(request,'StatusCallback')
		}
		if arg_name in validators:
			return validators[arg_name]
		else:
			return True, 0, ''

	def sanitize(self, request, arg_name, arg_value):
		sanitizers = {
			'To' : request.get('To',None),
			'From' : request.get('From',None),
			'Body' : request.get('Body',None),
			'StatusCallback' : request.get('StatusCallback',None)
		}
		if arg_name in sanitizers:
			return sanitizers[arg_name]
		else:
			return arg_value