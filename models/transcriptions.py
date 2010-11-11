from google.appengine.ext import db
from models import base
from hashlib import sha256
import random
import string
class Transcription(base.CommonModel):
	Text = db.TextProperty()
	CallSid = db.StringProperty()
	RecordingSid = db.StringProperty()

	@classmethod
	def new_Sid(self):
		return 'TR'+sha256(str(random())).hexdigest()