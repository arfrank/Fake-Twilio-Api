# http://www.twilio.com/docs/api/2010-04-01/rest/conference
from google.appengine.ext import db
from models import base
from hashlib import sha256
from random import random
import string
class Conference(base.CommonModel):
	"""
	Sid	A 34 character string that uniquely identifies this conference.
	FriendlyName	A user provided string that identifies this conference room.
	Status	A string representing the status of the conference. May be init, in-progress, or completed.
	DateCreated	The date that this conference was created, given as GMT in RFC 2822 format.
	DateUpdated	The date that this conference was last updated, given as GMT in RFC 2822 format.
	AccountSid	The unique id of the Account responsible for creating this conference.
	Uri	The URI for this resource, relative to https://api.twilio.com.
	"""
	
	FriendlyName = db.StringProperty()
	Status = db.StringProperty()
	AccountSid = db.StringProperty()
	
	@classmethod
	def new_Sid(self):
		return 'CF'+sha256(str(random())).hexdigest()

	def sanitize(self, request, arg_name, arg_value):
		sanitizers = {
			'FriendlyName' : request.get('FriendlyName','')
		}
		if arg_name in sanitizers:
			return sanitizers[arg_name]
		else:
			return arg_value

	def validate(self, request, arg_name,arg_value, **kwargs):
		validators = {
			'FriendlyName' : parameters.friendlyname_length(request.get('FriendlyName',''))
		}
		if arg_name in validators:
			return validators[arg_name]
		else:
			return True, 0, ''
