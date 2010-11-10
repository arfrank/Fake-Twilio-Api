from google.appengine.ext import db
from models import base
from random import random
from hashlib import sha256

from helpers import parameters

"""
Sid	A 34 character string that uniquely idetifies this resource.
DateCreated	The date that this resource was created, given as GMT RFC 2822 format.
DateUpdated	The date that this resource was last updated, given as GMT RFC 2822 format.
FriendlyName	A human readable descriptive text for this resource, up to 64 characters long. By default, the FriendlyName is a nicely formatted version of the phone number.
AccountSid	The unique id of the Account responsible for this phone number.
PhoneNumber	The incoming phone number. e.g., +16175551212 (E.164 format)
ApiVersion	Calls to this phone number will start a new TwiML session with this API version.
VoiceCallerIdLookup	Look up the caller's caller-ID name from the CNAM database (additional charges apply). Either true or false.
VoiceUrl	The URL Twilio will request when this phone number receives a call.
VoiceMethod	The HTTP method Twilio will use when requesting the above Url. Either GET or POST.
VoiceFallbackUrl	The URL that Twilio will request if an error occurs retrieving or executing the TwiML requested by Url.
VoiceFallbackMethod	The HTTP method Twilio will use when requesting the VoiceFallbackUrl. Either GET or POST.
StatusCallback	The URL that Twilio will request to pass status parameters (such as call ended) to your application.
StatusCallbackMethod	The HTTP method Twilio will use to make requests to the StatusCallback URL. Either GET or POST.
SmsUrl	The URL Twilio will request when receiving an incoming SMS message to this number.
SmsMethod	The HTTP method Twilio will use when making requests to the SmsUrl. Either GET or POST.
SmsFallbackUrl	The URL that Twilio will request if an error occurs retrieving or executing the TwiML from SmsUrl.
SmsFallbackMethod	The HTTP method Twilio will use when requesting the above URL. Either GET or POST.
Uri	The URI for this resource, relative to https://api.twilio.com.
"""
class Phone_Number(base.CommonModel):
	Sid = db.StringProperty()
	FriendlyName = db.StringProperty()
	AccountSid = db.StringProperty()
	PhoneNumber = db.StringProperty()
	ApiVersion = db.StringProperty()
	VoiceCallerIdLookup = db.BooleanProperty(default = False)
	VoiceUrl = db.StringProperty()
	VoiceMethod = db.StringProperty(default = 'POST')
	VoiceFallbackUrl = db.StringProperty()
	VoiceFallbackMethod = db.StringProperty(default = 'POST')
	StatusCallback = db.StringProperty()
	StatusCallbackMethod = db.StringProperty()
	SmsUrl = db.StringProperty()
	SmsMethod = db.StringProperty(default = 'POST')
	SmsFallbackUrl = db.StringProperty()
	SmsFallbackMethod = db.StringProperty(default = 'POST')

	@classmethod
	def new_Sid(self):
		return 'PN'+sha256(str(random())).hexdigest()

	#Validators for all properties that are user-editable.
	def validate(self, request, arg_name, arg_value):
		validators = {
			'FriendlyName' : parameters.friendlyname_length(request.get('FriendlyName','')),
			'VoiceCallerIdLookup' : parameters.allowed_boolean(request.get('VoiceCallerIdLookup',None)),
			'VoiceUrl' : parameters.standard_urls(request,'VoiceUrl'),
			'VoiceMethod' : parameters.phone_allowed_methods(arg_value,['GET','POST']),
			'VoiceFallbackUrl' : parameters.fallback_urls(request, 'VoiceFallbackUrl', 'VoiceUrl', self, 'Voice'),
			'VoiceFallbackMethod' : parameters.phone_allowed_methods(arg_value,['GET','POST']),
			'StatusCallback' : parameters.standard_urls(request,'StatusCallback'),
			'StatusCallbackMethod' : parameters.phone_allowed_methods(arg_value,['GET','POST']),
			'SmsUrl' : parameters.standard_urls(request,'SmsUrl'),
			'SmsMethod' : parameters.sms_allowed_methods(arg_value,['GET','POST']),
			'SmsFallbackUrl' : parameters.fallback_urls(request, 'SmsFallbackUrl', 'SmsUrl', self, 'SMS'),
			'SmsFallbackMethod' : parameters.sms_allowed_methods(arg_value,['GET','POST'])
		}

		if arg_name in validators:
			return validators[arg_name]
		else:
			return True, 0, ''
	#to be used, but for now will leave as is, minus standardizing how I do method saving
	def sanitize(self, request, arg_name, arg_value):
		sanitizers = {
			'FriendlyName' : request.get('FriendlyName',None),
			'VoiceCallerIdLookup' : request.get('VoiceCallerIdLookup',None),
			'VoiceUrl' : request.get('VoiceUrl',None),
			'VoiceMethod' : request.get('VoiceMethod','POST').upper(),
			'VoiceFallbackUrl' : request.get('VoiceFallbackUrl',None),
			'VoiceFallbackMethod' : request.get('VoiceFallbackMethod','POST').upper(),
			'StatusCallback' : request.get('StatusCallback',None),
			'StatusCallbackMethod' : request.get('StatusCallbackMethod','POST').upper(),
			'SmsUrl' : request.get('SmsUrl',None),
			'SmsMethod' : request.get('SmsMethod','POST').upper(),
			'SmsFallbackUrl' : request.get('SmsFallbackUrl',None),
			'SmsFallbackMethod' : request.get('SmsFallbackMethod','POST').upper()
		}
		if arg_name in sanitizers:
			return sanitizers[arg_name]
		else:
			return arg_value