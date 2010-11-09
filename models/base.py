from google.appengine.ext import db
import datetime
import logging

class CommonModel(db.Model):
	DateCreated = db.DateTimeProperty(auto_now_add = True)
	DateUpdated = db.DateTimeProperty(auto_now = True)
	
	def get_dict(self):
		object_dict = {}
		for key in self.properties():
			#Hide private properties to allow for storing private things
			if key[0] != '_':
				if type(getattr(self,key)) == datetime.datetime:
					#not given twilio format, but shouldnt really break it for anyone really, will fix later
					object_dict[key] = getattr(self,key).isoformat()
					#.strpformat('%M-%D-%Y %H:%I:%S %z) #not right
				else:
					object_dict[key] = getattr(self,key)	
		return object_dict

	@classmethod
	def new(cls, request, AccountSid = None, **kwargs):
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
		if hasattr(cls,'AccountSid') and AccountSid is not None:
			property_dictionary['AccountSid'] = AccountSid
		if Valid:
			Sid = cls().new_Sid()
			return cls(
						Sid = Sid,
						**property_dictionary
					), True, 0, ''
		else:
			return '', False, TwilioCode, TwilioMsg


# Base functions to be overloaded to ensure that they exist
	def sanitize(self, request, arg_name, arg_value):
		return arg_value

	def validate(self, request, arg_name, arg_value):
		return True