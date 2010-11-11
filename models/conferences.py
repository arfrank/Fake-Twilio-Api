from google.appengine.ext import db
from models import base
from hashlib import sha256
import random
import string
class Conference(base.CommonModel):

	
	@classmethod
	def new(cls, key_name, email, password):
		Sid = 'CF'+sha256(email).hexdigest()
		return cls(Sid=Sid)


	@classmethod
	def new_Sid(self):
		return 'CF'+sha256(str(random())).hexdigest()
