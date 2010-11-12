from google.appengine.ext import db
from models import base
from hashlib import sha256
from random import random
import string

class Twiml(base.CommonModel):
	AccountSid = db.StringProperty()
	Text = db.TextProperty()
	Twiml = db.BlobProperty() #pickled since its a list, 0,0 means first child of first element
	Current = db.ListProperty(int, default = []) 
	Initial = db.BooleanProperty(default = True)
	CallSid = db.StringProperty()
	SmsSid = db.StringProperty()

	@classmethod
	def new_Sid(self):
		return 'TW'+sha256(str(random())).hexdigest()