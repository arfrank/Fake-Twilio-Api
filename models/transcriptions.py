from google.appengine.ext import db
from models import base
from hashlib import sha256
from random import random
import string

"""
Sid	A 34 character string that uniquely identifies this resource.
DateCreated	The date that this resource was created, given in RFC 2822 format.
DateUpdated	The date that this resource was last updated, given in RFC 2822 format.
AccountSid	The unique id of the Account responsible for this transcription.
Status	A string representing the status of the transcription: in-progress, completed or failed.
RecordingSid	The unique id of the Recording this Transcription was made of.
Duration	The duration of the transcribed audio, in seconds.
TranscriptionText	The text content of the transcription.
Price	The charge for this transcript in USD. Populated after the transcript is completed. Note, this value may not be immediately available.
Uri
"""
class Transcription(base.CommonModel):
	AccountSid = db.StringProperty()
	Status = db.StringProperty()
	RecordingSid = db.StringProperty()
	Duration = db.IntegerProperty()
	TranscriptionText = db.TextProperty()
	Price = db.FloatProperty()

	@classmethod
	def new_Sid(self):
		return 'TR'+sha256(str(random())).hexdigest()