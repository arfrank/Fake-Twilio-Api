from google.appengine.ext import db
from models import base
from hashlib import sha256
from random import random
import string
import datetime

from helpers import parameters

from google.appengine.api.labs import taskqueue
from google.appengine.api import urlfetch


"""
Sid	A 34 character string that uniquely identifies this resource.
ParentCallSid	A 34 character string that uniquely identifies the call that created this leg.
AccountSid	The unique id of the Account responsible for creating this call.
To	The phone number that received this call. e.g., +16175551212 (E.164 format)
From	The phone number that made this call. e.g., +16175551212 (E.164 format)
PhoneNumberSid	If the call was inbound, this is the Sid of the IncomingPhoneNumber that received the call. If the call was outbound, it is the Sid of the OutgoingCallerId from which the call was placed.
Status	A string representing the status of the call. May be queued, ringing, in-progress, completed, failed, busy or no-answer.
StartTime	The start time of the call, given as GMT in RFC 2822 format. Empty if the call has not yet been dialed.
EndTime	The end time of the call, given as GMT in RFC 2822 format. Empty if the call did not complete successfully.
Duration	The length of the call in seconds. This value is empty for busy, failed, unanswered or ongoing calls.
Price	The charge for this call in USD. Populated after the call is completed. May not be immediately available.
Direction	A string describing the direction of the call. inbound for inbound calls, outbound-api for calls initiated via the REST API or outbound-dial for calls initiated by a <Dial> verb.
AnsweredBy	If this call was initiated with answering machine detection, either human or machine. Empty otherwise.
ForwardedFrom	If this call was an incoming call forwarded from another number, the forwarding phone number (depends on carrier supporting forwarding). Empty otherwise.
CallerName	If this call was an incoming call from a phone number with Caller ID Lookup enabled, the caller's name. Empty otherwise.
"""

class Call(base.CommonModel):
	AccountSid = db.StringProperty()
	To = db.StringProperty()
	From = db.StringProperty()
	PhoneNumberSid = db.StringProperty()
	Status = db.StringProperty()
	StartTime = db.DateTimeProperty()
	EndTime = db.DateTimeProperty()
	Duration = db.IntegerProperty()
	Price = db.FloatProperty()
	Direction = db.StringProperty()
	AnsweredBy = db.StringProperty()
	ForwardedFrom = db.StringProperty()
	CallerName = db.StringProperty()
	
	"""
	#No longer needed!
	@classmethod
	def new(cls, ParentCallSid, AccountSid,To,From,PhoneNumberSid,Status,StartTime = None,EndTime = None,Duration = None,Price = None,Direction,AnsweredBy = None,ForwardedFrom = None,CallerName = None):
		Sid = 'CA'+sha256(email).hexdigest()
		return cls(	Sid=Sid,
					ParentCallSid = ParentCallSid,
					AccountSid = AccountSid,
					To = To,
					From = From,
					PhoneNumberSid = PhoneNumberSid,
					Status = Status,
					StartTime = StartTime,
					EndTime = EndTime,
					Duration = Duration,
					Price = Price,
					Direction = Direction,
					AnsweredBy = AnsweredBy,
					ForwardedFrom = ForwardedFrom,
					CallerName = CallerName
				)
	"""
	
	def validate(self, request, arg_name,arg_value, **kwargs):
		validators = {
			'To' : parameters.valid_to_phone_number(arg_value if arg_value is not None else request.get('To',None),required=True),
			'From' : parameters.valid_from_phone_number(arg_value if arg_value is not None else request.get('From',None),required=True, Direction = kwargs['Direction'] if 'Direction' in kwargs else None)
		}
		if arg_name in validators:
			return validators[arg_name]
		else:
			return True, 0, ''

	def sanitize(self, request, arg_name, arg_value):
		sanitizers = {
			'To' : arg_value if (arg_value is not None or request is None) else request.get('To',None),
			'From' : arg_value if (arg_value is not None or request is None) else request.get('From',None),
		}
		if arg_name in sanitizers:
			return sanitizers[arg_name]
		else:
			return arg_value
	
	@classmethod
	def new_Sid(self):
		return 'CA'+sha256(str(random())).hexdigest()

	
	def ring(self):
		self.Status = 'ringing'
		self.put()

	def connect(self):#, Instance, request):
		self.Status = 'in-progress'
		self.StartTime = datetime.datetime.now()
		#get url of twiml
		#twiml = urlfetch.urlfetch(request.get('Url'),method = urlfetch.POST)
		#if that fails, fallback, if not fallback goto phone number url?
		
		#parse twiml and do things according to that
		self.put()

	def failed(self):
		self.Status = 'failed'
		self.Price = 0.00
		self.put()

	def busy(self):
		self.Status = 'busy'
		self.Price = 0.00
		self.put()

	def no_answer(self):
		self.Status = 'no-answer'
		self.Price = 0.00
		self.put()

	def disconnect(self,StatusCallback = None,StatusCallbackMethod = 'POST'):
		self.Status = 'complete'
		self.EndTime = datetime.datetime.now()
		self.Duration = (self.EndTime - self.StartTime).seconds
		if self.Direction == 'outbound-api' or self.Direction == 'outbound-dial':
			#should be dependent on country code, but will need more work
			self.Price = self.Duration * (0.02)
		elif self.Direction == 'inbound':
			self.Price = self.Duration * (0.01)
		try:
			self.put()
		except Exception, e:
			return False
		else:
			if StatusCallback is not None:
				try:
					taskqueue.Queue('StatusCallbacks').add(taskqueue.Task(url='/Callbacks/Call', params = {'CallSid':self.Sid,'StatusCallback':StatusCallback,'StatusCallbackMethod':StatusCallbackMethod}))
				except Exception, e:
					pass
			return True