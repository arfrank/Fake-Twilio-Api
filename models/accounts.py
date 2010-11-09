from google.appengine.ext import db
from models import base
from hashlib import sha256
import random
import string
class Account(base.CommonModel):
	Sid = db.StringProperty()
	FriendlyName = db.StringProperty()
	Status = db.StringProperty()
	AuthToken = db.StringProperty()
	Salt = db.StringProperty()
	Email = db.EmailProperty()
	Password = db.StringProperty()
	
	@classmethod
	def new(cls, key_name, email, password):
		Salt = ''.join(random.choice(string.digits) for x in range(32))
		Sid = 'AC'+sha256(email).hexdigest()
		Password = sha256(Sid+password+Salt).hexdigest()
		AuthToken = sha256(Sid+Password).hexdigest()
		return cls(key_name=email,Email = email, FriendlyName = email,
					Sid=Sid,Status='Active',Salt=Salt,
					Password=Password,AuthToken=AuthToken)
	
	def check_password(self,password):
		return self.Password == sha256(self.Sid+password+self.Salt).hexdigest()
		
	@classmethod
	def new_Sid(self):
		return 'AC'+sha256(str(random())).hexdigest()
