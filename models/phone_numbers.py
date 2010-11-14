from google.appengine.ext import db
from models import base
from random import random
from hashlib import sha256

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
	def validate(self, request, arg_name, arg_value, **kwargs):
		from helpers import parameters
		
		validators = {
			'FriendlyName' : parameters.friendlyname_length(parameters.arg_or_request(arg_value, request, arg_name)),

			'VoiceCallerIdLookup' : parameters.allowed_boolean(parameters.arg_or_request(arg_value, request, arg_name,False)),

			'VoiceUrl' : parameters.standard_urls(parameters.arg_or_request(arg_value, request, arg_name)),

			'VoiceMethod' : parameters.phone_allowed_methods(parameters.arg_or_request(arg_value, request, arg_name,'POST'),['GET','POST']),

			'VoiceFallbackUrl' : parameters.fallback_urls(parameters.arg_or_request(arg_value, request, arg_name,''), parameters.arg_or_request(arg_value, request, 'VoiceUrl',''), 'VoiceUrl', self, 'Voice'),

			'VoiceFallbackMethod' : parameters.phone_allowed_methods(parameters.arg_or_request(arg_value, request, arg_name,'POST'),['GET','POST']),

			'StatusCallback' : parameters.standard_urls(parameters.arg_or_request(arg_value, request, arg_name)),

			'StatusCallbackMethod' : parameters.phone_allowed_methods(parameters.arg_or_request(arg_value, request, arg_name,'POST'),['GET','POST']),

			'SmsUrl' : parameters.standard_urls(parameters.arg_or_request(arg_value, request, arg_name)),

			'SmsMethod' : parameters.sms_allowed_methods(parameters.arg_or_request(arg_value, request, arg_name,'POST'),['GET','POST']),

			'SmsFallbackUrl' : parameters.fallback_urls(parameters.arg_or_request(arg_value, request, arg_name,''), parameters.arg_or_request(arg_value, request, 'SmsUrl',''), 'SmsUrl', self, 'SMS'),

			'SmsFallbackMethod' : parameters.sms_allowed_methods(parameters.arg_or_request(arg_value, request, arg_name,'POST'),['GET','POST'])

		}

		if arg_name in validators:
			return validators[arg_name]
		else:
			return True, 0, ''
	#to be used, but for now will leave as is, minus standardizing how I do method saving
	def sanitize(self, request, arg_name, arg_value):
		from helpers import parameters
		
		sanitizers = {
			'FriendlyName' : parameters.arg_or_request(arg_value, request, arg_name),
			'VoiceCallerIdLookup' : parameters.arg_or_request(arg_value, request, arg_name,False),
			'VoiceUrl' : parameters.arg_or_request(arg_value, request, arg_name),
			'VoiceMethod' : parameters.arg_or_request(arg_value, request, arg_name,'POST').upper(),
			'VoiceFallbackUrl' : parameters.arg_or_request(arg_value, request, arg_name),
			'VoiceFallbackMethod' : parameters.arg_or_request(arg_value, request, arg_name,'POST').upper(),
			'StatusCallback' : parameters.arg_or_request(arg_value, request, arg_name),
			'StatusCallbackMethod' : parameters.arg_or_request(arg_value, request, arg_name,'POST').upper(),
			'SmsUrl' :parameters.arg_or_request(arg_value, request, arg_name),
			'SmsMethod' : parameters.arg_or_request(arg_value, request, arg_name,'POST').upper(),
			'SmsFallbackUrl' : parameters.arg_or_request(arg_value, request, arg_name),
			'SmsFallbackMethod' : parameters.arg_or_request(arg_value, request, arg_name,'POST').upper()
		}
		if arg_name in sanitizers:
			return sanitizers[arg_name]
		else:
			return arg_value