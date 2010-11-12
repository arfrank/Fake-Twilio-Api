from google.appengine.ext import db
from models import base
from hashlib import sha256
from random import random

from models import transcriptions

from google.appengine.api.labs import taskqueue


import string
"""
Sid	A 34 character string that uniquely identifies this resource.
DateCreated	The date that this resource was created, given in RFC 2822 format.
DateUpdated	The date that this resource was last updated, given in RFC 2822 format.
AccountSid	The unique id of the Account responsible for this recording.
CallSid	The call during which the recording was made.
Duration	The length of the recording, in seconds.
ApiVersion	The version of the API in use during the recording.
Uri	The URI for this resource, relative to https://api.twilio.com
SubresourceUris	The list of subresources under this account
"""

class Recording(base.CommonModel):
	AccountSid = db.StringProperty()
	CallSid = db.StringProperty()
	Duration = db.IntegerProperty()

	@classmethod
	def new_Sid(self):
		return 'RE'+sha256(str(random())).hexdigest()
		
	def transcribe(self,callbackUrl = None):
		Trans,Valid, TwilioCode, TwilioMsg = transcriptions.Transcription.new(
			AccoundSid = self.AccountSid,
			request = None,
			Duratation = self.Duration,
			RecordingSid = self.Sid,
			Status = 'in-progress',
			TranscribeText = 'Lorem Ipsum',
			Price = self.Duration * (0.05)
		)
		Trans.put()
		if callbackUrl is not None:
			try:
				taskqueue.Queue( 'StatusCallbacks' ).add( taskqueue.Task( url='/Callbacks/Transcription', params = { 'TranscriptionSid' : Trans.Sid } ) )
			except Exception, e:
				pass
			