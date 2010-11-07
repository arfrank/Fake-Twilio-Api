from google.appengine.ext import db
from models import base
from hashlib import sha256
import random
import string
class Recording(base.CommonModel):
	Sid = db.StringProperty()

	
	@classmethod
	def new(cls, key_name, email, password):
		Sid = 'RE'+sha256(email).hexdigest()
		return cls(Sid=Sid)
