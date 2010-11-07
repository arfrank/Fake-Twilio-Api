from google.appengine.ext import db
from models import base
from random import random
from hashlib import sha256

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