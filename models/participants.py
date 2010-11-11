# http://www.twilio.com/docs/api/2010-04-01/rest/participant
from google.appengine.ext import db
from models import base
from hashlib import sha256
import random
import string
class Participant(base.CommonModel):
	"""
	CallSid	A 34 character string that uniquely identifies the call that is connected to this conference
	ConferenceSid	A 34 character string that identifies the conference this participant is in
	DateCreated	The date that this resource was created, given in RFC 2822 format.
	DateUpdated	The date that this resource was last updated, given in RFC 2822 format.
	AccountSid	The unique id of the Account that created this conference
	Muted	true if this participant is currently muted. false otherwise.
	StartConferenceOnEnter	Was the startConferenceOnEnter attribute set on this participant (true or false)?
	EndConferenceOnExit	Was the endConferenceOnExit attribute set on this participant (true or false)?
	Uri	The URI for this resource, relative to https://api.twilio.com.
	"""
	
	CallSid = db.StringProperty()
	ConferenceSid = db.StringProperty()
	AccountSid = db.StringProperty()
	Muted = db.StringProperty()
	StartConferenceOnEnter = db.BooleanProperty()
	EndConferenceOnExit = db.BooleanProperty()
	
	@classmethod
	def new_Sid(self):
		#Useless, but it might come in handy some day
		return 'PA'+sha256(str(random())).hexdigest()

	def sanitize(self, request, arg_name, arg_value):
		sanitizers = {
		}
		if arg_name in sanitizers:
			return sanitizers[arg_name]
		else:
			return arg_value

	def validators(self, request, arg_name, arg_value):
		validators = {
		}
		if arg_name in validators:
			return validators[arg_name]
		else:
			return True, 0, ''
