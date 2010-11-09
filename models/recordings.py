from google.appengine.ext import db
from models import base
from hashlib import sha256
import random
import string
class Recording(base.CommonModel):
	Sid = db.StringProperty()
	AccountSid = db.StringProperty()
	CallSid = db.StringProperty()
	

	@classmethod
	def new_Sid(self):
		return 'RE'+sha256(str(random())).hexdigest()
