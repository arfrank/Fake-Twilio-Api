from google.appengine.ext import db
from models import base
from hashlib import sha256

from random import random, choice

import string

import logging

from helpers import parameters

class Account(base.CommonModel):
	FriendlyName = db.StringProperty()
	Status = db.StringProperty()
	AuthToken = db.StringProperty()
	Salt = db.StringProperty()
	Email = db.EmailProperty()
	Password = db.StringProperty()	
	
	@classmethod
	def new(cls, key_name, email, password):
		Salt = ''.join(choice(string.digits) for x in range(32))
		Sid = 'AC'+sha256(email).hexdigest()
		Password = sha256(Sid+password+Salt).hexdigest()
		AuthToken = sha256(Sid+Password).hexdigest()
		return cls(key_name=email,Email = email, FriendlyName = email,
					Sid=Sid,Status='active',Salt=Salt,
					Password=Password,AuthToken=AuthToken)
	
	def check_password(self,password):
		return self.Password == sha256(self.Sid+password+self.Salt).hexdigest()
		
	@classmethod
	def new_Sid(self):
		return 'AC'+sha256(str(random())).hexdigest()

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
			'FriendlyName' : parameters.friendlyname_length(parameters.arg_or_request(arg_value, request, arg_name,''))
		}
		if arg_name in validators:
			
			return validators[arg_name]
		else:
			return True, 0, ''
