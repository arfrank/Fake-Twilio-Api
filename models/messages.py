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
	def new(cls,To,From,Body,AccountSid,Direction,Status,Price=None,StatusCallback = None):
		Sid = 'SM'+sha256(To+str(random())+From).hexdigest()
		return cls(To=To,From=From,Body=Body,AccountSid=AccountSid,Direction=Direction,Status=Status,Price = Price,Sid = Sid,StatusCallback = StatusCallback)

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
			'FriendlyName' : request.get('FriendlyName',None),
			'VoiceCallerIdLookup' : parameters.allowed_boolean(request.get('VoiceCallerIdLookup',None)),
			'VoiceUrl' : parameters.standard_urls(request.get('VoiceUrl',None)),
			'VoiceMethod' : parameters.allowed_methods(arg_value,['GET','POST']),
			'VoiceFallbackUrl' : request.get('VoiceFallbackUrl',None),
			'VoiceFallbackMethod' : parameters.allowed_methods(arg_value,['GET','POST']),
			'StatusCallback' : request.get('StatusCallback',None),
			'StatusCallbackMethod' : parameters.allowed_methods(arg_value,['GET','POST']),
			'SmsUrl' : request.get('SmsUrl',None),
			'SmsMethod' : parameters.allowed_methods(arg_value,['GET','POST']),
			'SmsFallbackUrl' : request.get('SmsFallbackUrl',None),
			'SmsFallbackMethod' : parameters.allowed_methods(arg_value,['GET','POST'])
		}

		return True

	def sanitize(self, request, arg_name, arg_value):
		santizers = {
			'FriendlyName' : self.request.get('FriendlyName',None),
			'VoiceCallerIdLookup' : self.request.get('VoiceCallerIdLookup',None),
			'VoiceUrl' : self.request.get('VoiceUrl',None),
			'VoiceMethod' : parameters.methods(arg_name,self.request,'POST'),
			'VoiceFallbackUrl' : self.request.get('VoiceFallbackUrl',None),
			'VoiceFallbackMethod' : parameters.methods(arg_name,self.request,'POST'),
			'StatusCallback' : self.request.get('StatusCallback',None),
			'StatusCallbackMethod' : parameters.methods(arg_name,self.request,'POST'),
			'SmsUrl' : self.request.get('SmsUrl',None),
			'SmsMethod' : parameters.methods(arg_name,self.request,'POST'),
			'SmsFallbackUrl' : self.request.get('SmsFallbackUrl',None),
			'SmsFallbackMethod' : parameters.methods(arg_name,self.request,'POST')
		}
		return arg_value