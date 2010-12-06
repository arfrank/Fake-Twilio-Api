#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

import pickle

import os

import urllib, urllib2, base64, hmac
import logging

from django.utils import simplejson

from libraries.gaesessions import get_current_session

from models import accounts, incoming_phone_numbers, outgoing_caller_ids, phone_numbers, calls, messages, twimls

from helpers import application, authorization, request, twiml, parameters, phone_number_helper as pn_helper

from decorators import webapp_decorator

class MainHandler(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), '../templates/home.html')
		self.response.out.write(template.render(path,{}))

class Register(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), '../templates/register.html')
		self.response.out.write(template.render(path,{}))

	def post(self):
		from hashlib import sha256
		required = ['email','password','password_confirm']
		if application.required(required,self.request) and self.request.get('password') == self.request.get('password_confirm'):
			exist_account = accounts.Account.get_by_key_name(self.request.get('email'))
			if exist_account is None:
				account = accounts.Account.new(key_name = self.request.get('email').lower(), email=self.request.get('email').lower(),password=self.request.get('password'))
				account.put()
				session = get_current_session()
				session.regenerate_id()
				session['Account'] = account
				self.redirect('/account')
			else:
				Register.get(self)
		else:
			Register.get(self)
		

class Login(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), '../templates/login.html')
		self.response.out.write(template.render(path,{}))

	def post(self):
		required = ['email','password']
		if application.required(required,self.request):
			Account = accounts.Account.get_by_key_name(self.request.get('email'))
			if Account is not None and Account.check_password(self.request.get('password')):
				session = get_current_session()
				session.regenerate_id()
				session['Account'] = Account
				self.redirect('/account')
			else:
				Login.get(self)

class Account(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self):
		path = os.path.join(os.path.dirname(__file__), '../templates/account.html')
		self.response.out.write(template.render(path,{'data':self.data}))

class PhoneNumbers(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self):

		self.data['PhoneNumbers'] = incoming_phone_numbers.Incoming_Phone_Number.all().filter('AccountSid =',self.data['Account'].Sid)
		path = os.path.join(os.path.dirname(__file__), '../templates/phone-numbers.html')
		self.response.out.write(template.render(path,{'data':self.data}))

	@webapp_decorator.check_logged_in
	def post(self):
		phone_number, Valid, phoneGroups = pn_helper.parse_phone_number(self.request.get('phone_number'))
		if Valid and len(phone_number) == 12:
			PhoneNumber, Valid, TwilioCode, TwilioMsg = incoming_phone_numbers.Incoming_Phone_Number.new(PhoneNumber = phone_number, AccountSid = self.data['Account'].Sid, ApiVersion = '2010-04-01', request = self.request)
			if Valid:
				PhoneNumber.put()
		PhoneNumbers.get(self)

class PhoneNumber(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self,Sid):
		Sid = urllib.unquote(Sid)

		self.data['PhoneNumber'] = incoming_phone_numbers.Incoming_Phone_Number.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Sid = ',Sid).get()

		if self.data['PhoneNumber'] is not None:
			path = os.path.join(os.path.dirname(__file__), '../templates/phone-number.html')
			self.response.out.write(template.render(path,{'data':self.data}))
		else:
			self.redirect('/phone-numbers')

	@webapp_decorator.check_logged_in
	def post(self,Sid):
		Sid = urllib.unquote(Sid)

		self.data['PhoneNumber'] = incoming_phone_numbers.Incoming_Phone_Number.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Sid = ',Sid).get()

		if self.data['PhoneNumber'] is not None:
			Valid = True
			for arg in self.request.arguments():
				if Valid:
					Valid,TwilioCode,TwilioMsg =  self.data['PhoneNumber'].validate(self.request, arg, self.request.get( arg ,None))
				setattr(self.data['PhoneNumber'], arg, self.data['PhoneNumber'].sanitize( self.request, arg, self.request.get( arg ,None)))
					
			if Valid:
				self.data['PhoneNumber'].put()
			else:
				self.data['Error'] = True
				self.data['TwilioCode'] = TwilioCode
				self.data['TwilioMsg'] = TwilioMsg
			path = os.path.join(os.path.dirname(__file__), '../templates/phone-number.html')
			self.response.out.write(template.render(path,{'data':self.data}))
		else:
			self.redirect('/phone-numbers')
		
class FakeInbound(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self, Sid):
		Sid = urllib.unquote(Sid)
		self.data['PhoneNumber'] = incoming_phone_numbers.Incoming_Phone_Number.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Sid = ',Sid).get()
		if self.data['PhoneNumber'] is not None:
			path = os.path.join(os.path.dirname(__file__), self.get_template)
			self.response.out.write(template.render(path,{'data':self.data}))
		else:
			self.redirect('/phone-numbers')

	@webapp_decorator.check_logged_in
	def post(self,Sid):
		Sid = urllib.unquote(Sid)
		self.data['PhoneNumber'] = incoming_phone_numbers.Incoming_Phone_Number.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Sid = ',Sid).get()
		if self.data['PhoneNumber'] is not None:
			
			#########Doing webapp error checking!
			Valid = True
			Any = False
			Blank = False
			for param in self.REQUIRED:
				if self.request.get(param,'') == '':
					logging.info('Missing Required Parameter'+ param)
					Valid = False
			for param in self.ALLOWED_PARAMETERS:
				if self.request.get(param,'') != '':
					logging.info('Have optional parameter'+ param)
					Any = True
				else:
					Blank = True
			if Valid and (Any and Blank):
				Valid = False
			if Valid:
			### ERROR CHECKING DONE FOR PASSED IN
				Instance, Valid, self.data['TwilioCode'],self.data['TwilioMsg'] = self.Instance.new(
											To = self.data['PhoneNumber'].PhoneNumber,
											From = self.request.get('From'),
											Body = self.request.get('Body') if self.SMS else None,
											request = self.request,
											AccountSid = self.data['Account'].Sid,
											Direction = 'incoming',
											Status = 'sent' if self.SMS else 'queued'
										)
				#CHECK IF WE'VE PASSED VALID INFO TO MESSAGE
				if Valid:
					Instance.put()
					Payload = Instance.get_dict()
					#This is some really really bad bad form processing

					#Payload = {}
					for param in self.ALLOWED_PARAMETERS:
						Payload[param] = self.request.get(param,'')
					for k in Payload:
						if Payload[k] is None:
							Payload[k] = ''
					#has to have a smsurl, not necessarily fallback url
					# GET THE TWIML URLS
					self.data['Response'] = request.request_twiml(self.data['Account'], getattr( self.data['PhoneNumber'], self.InstanceMain[0]), getattr( self.data['PhoneNumber'], self.InstanceMain[1] ), Payload)

					if 200<= self.data['Response'].status_code <= 300:
						logging.info('normal response')
						Valid, TwimlText, self.data['TwilioCode'], self.data['TwilioMsg'] = twiml.check_twiml_content_type( self.data['Response'] )
						logging.info(self.request.headers)
						if Valid:
							logging.info('Valid twiml check for content-type')
							Valid, self.data['twiml_object'], self.data['TwilioCode'], self.data['TwilioMsg'] = twiml.parse_twiml(TwimlText, sms = False)

							Url = getattr( self.data['PhoneNumber'], self.InstanceMain[0] )

					elif 400 <= self.data['Response'].status_code <= 600 or Valid == False:

						#bad response and see if there is a fallback and repeat	or bad twiml

						if getattr( self.data['PhoneNumber'], self.InstanceFallback[0] ) is not None and getattr( self.data['PhoneNumber'], self.InstanceFallback[0] ) != '':

							self.data['FallbackResponse'] = request.request_twiml(self.data['Account'], getattr( self.data['PhoneNumber'], self.InstanceFallback[0] ), getattr( self.data['PhoneNumber'], self.InstanceFallback[1] ), Payload)

							if 200 <= self.data['FallbackResponse'].status_code <=300:

								Valid, TwimlText, self.data['TwilioCode'], self.data['TwilioMsg'] = twiml.check_twiml_content_type( self.data['FallbackResponse'] )
								if Valid:

									Valid, self.data['twiml_object'], self.data['TwilioCode'], self.data['TwilioMsg']  = twiml.parse_twiml(TwimlText, sms = True)

									Url = getattr( self.data['PhoneNumber'], self.InstanceFallback[0] )

					if Valid:

						#logging.info(TwimlText)

						#Always returns model object, validity, errorcode, msg
						Twiml, Valid, self.data['TwilioCode'], self.data['TwilioMsg']  = twimls.Twiml.new(
							request = self.request,
							Url = Url,
							AccountSid = self.data['Account'].Sid,
							Twiml = pickle.dumps(self.data['twiml_object']),
							Current = [],
							CallSid = Instance.Sid if self.SMS == False else None,
							MessageSid = Instance.Sid if self.SMS == True else None
						)
						#logging.info(Twiml)
						Twiml.put()
						self.data['Twiml'] = Twiml
					#parse the twiml and do some fake things
					path = os.path.join(os.path.dirname(__file__), self.post_template)
					self.response.out.write(template.render(path,{'data':self.data}))
				else:
					self.data['Arguments'] = {}
					for key in self.request.arguments():
						self.data['Arguments'][key] = self.request.get(key,'')
					FakeInbound.get(self,Sid)
			else:
				self.data['Arguments'] = {}
				for key in self.request.arguments():
					self.data['Arguments'][key] = self.request.get(key,'')
				FakeInbound.get(self,Sid)
		else:
			self.redirect('/phone-numbers')

class FakeSms(FakeInbound):
	def __init__(self):
		self.get_template = '../templates/fake-sms.html'
		self.post_template = '../templates/fake-sms-result.html'
		self.InstanceMain = ['SmsUrl', 'SmsMethod']
		self.InstanceFallback = ['SmsFallbackUrl', 'SmsFallbackMethod']
		self.REQUIRED = ['From','Body']
		self.ALLOWED_PARAMETERS = ['FromCity','FromState','FromZip','FromCounty','ToCity','ToState','ToZip','ToCounty']
		self.Instance = messages.Message
		self.SMS = True


class FakeVoice(FakeInbound):
	"""
	Parameter	Description
	CallSid	A unique identifier for this call, generated by Twilio.
	AccountSid	Your Twilio account id. It is 34 characters long, and always starts with the letters AC.
	From	The phone number of the party that initiated the call. Formatted with a '+' and country code e.g., +16175551212 (E.164 format). If the call is inbound, then it is the caller's caller ID. If the call is outbound, i.e., initiated via a request to the REST API, then this is the phone number you specify as the caller ID.
	To	The phone number of the called party. Formatted with a '+' and country code e.g., +16175551212 (E.164 format). If the call is inbound, then it's your Twilio phone number. If the call is outbound, then it's the phone number you provided to call.
		CallStatus	A descriptive status for the call. The value is one of queued, ringing, in-progress, completed, busy, failed or no-answer. See the CallStatus section below for more details.
		ApiVersion	The version of the Twilio API used to handle this call. For incoming calls, this is determined by the API version set on the called number. For outgoing calls, this is the API version used by the outgoing call's REST API request.
		Direction	Indicates the direction of the call. In most cases this will be inbound, but if you are using <Dial> it will be outbound-dial.
		ForwardedFrom	This parameter is set only when Twilio receives a forwarded call, but its value depends on the caller's carrier including information when forwarding. Not all carriers support passing this information.
		"""

	def __init__(self):
		self.get_template = '../templates/fake-voice.html'
		self.post_template = '../templates/fake-voice-result.html'
		self.InstanceMain = ['VoiceUrl', 'VoiceMethod']
		self.InstanceFallback = ['VoiceFallbackUrl', 'VoiceFallbackMethod']
		self.REQUIRED = ['From']
		self.ALLOWED_PARAMETERS = ['FromCity','FromState','FromZip','FromCounty','ToCity','ToState','ToZip','ToCounty']
		self.Instance = calls.Call
		self.SMS = False


##########################################################################################################################


class Calls(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self):
		self.data['QueuedCalls'] = calls.Call.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Status = ','queued').get()
		self.data['RingingCalls'] = calls.Call.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Status = ','ringing').get()
		self.data['InProgressCalls'] = calls.Call.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Status = ','in-progress').get()
		self.data['CompletedCalls'] = calls.Call.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Status = ','completed').get()
		self.data['BusyCalls'] = calls.Call.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Status = ','busy').get()
		self.data['NoAnswerCalls'] = calls.Call.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Status = ','no-answer').get()
		self.data['CanceledCalls'] = calls.Call.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Status = ','canceled').get()
		path = os.path.join(os.path.dirname(__file__), '../templates/calls.html')
		self.response.out.write(template.render(path,{'data':self.data}))
		
class TwimlHandler(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def post(self,Sid):
		
		Twiml = twimls.Twiml.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Sid = ',Sid).get()
		if Twiml is not None:
			logging.info(Twiml.CallSid)
			logging.info(Twiml.SmsSid)
			if Twiml.CallSid is not None:
				Original = calls.Call.all().filter('Sid = ',Twiml.CallSid).get()
				logging.info('Original')
				logging.info(Original)
			elif Twiml.SmsSid is not None:
				Original = messages.Message.all().filter('Sid = ',Twiml.SmsSid).get()

			I,C = 0,0 #index, child for lists later to store status

			Twiml_obj = pickle.loads(Twiml.Twiml)

			response = ''

			newTwiml = None

			if not Twiml.Initial:

				I = Twiml.Current[0]
			else:

				Twiml.Initial = False

			# process list items until need a response?
			logging.info(Twiml_obj)

			while I < len(Twiml_obj):
				#get the response, whether or not to keep processing, and if the newTwiml document exists
				twiml_response, Break, newTwiml = twiml.process_verb(Twiml_obj[I], Twiml, Original, self.request.get('input',''))

				response += str(twiml_response) + '\n'

				if Break:
					#Check to see if its the final break; hangup, reject
					if Twiml_obj[I]['Type'] == 'Hangup' or Twiml_obj[I] == 'Reject':

						I = len(Twiml_obj)

					break

				I+=1

			if I == len(Twiml_obj):

				response+='You have reached the end of that Twiml Document\n'

			response_data = {'Text': response }

			if newTwiml:

				response_data['TwimlSid'] = newTwiml.Sid

			Twiml.Current = [I]

			Twiml.put()

			self.response.out.write(simplejson.dumps(response_data))

		else:

			self.response.set_status(404)
		
class Call(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self,Sid):
		Sid = urllib.unquote(Sid)
		self.data['Call'] = calls.Call.all().filter('AccountSid = ',self.data['Account'].Sid).filter('Sid = ',Sid).get()
		if self.data['Call'] is not None:
			path = os.path.join(os.path.dirname(__file__), '../templates/call.html')
			self.response.out.write(template.render(path,{'data':self.data}))
		else:
			self.redirect('/calls')

class Test(webapp.RequestHandler):
	from random import random
	try:
		response = twiml.parse_twiml("""<?xml version="1.0" encoding="UTF-8" ?><Response><Play>http://foo.com/cowbell.mp3</Play><Gather></Gather><Say>This it another child</Say><Gather><Say>Press 1</Say></Gather></Response>""")
		print response
	except Exception, e:
		print e

class CallerIds(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self):
		self.data['PhoneNumbers'] = outgoing_caller_ids.Outgoing_Caller_Id.all().filter('AccountSid =',self.data['Account'].Sid)
		path = os.path.join(os.path.dirname(__file__), '../templates/caller-ids.html')
		self.response.out.write(template.render(path,{'data':self.data}))

class CallerId(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self, Sid):
		path = os.path.join(os.path.dirname(__file__), '../templates/caller-id.html')
		self.response.out.write(template.render(path,{'data':self.data}))

class Examples(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self):
		import urlparse
		self.data['host'] = urlparse.urlparse(self.request.url).netloc
		path = os.path.join(os.path.dirname(__file__), '../templates/examples.html')
		self.response.out.write(template.render(path,{'data':self.data}))

class Logout(webapp.RequestHandler):
	def get(self):
		session = get_current_session()
		session.terminate()
		self.redirect('/')

def main():
	application = webapp.WSGIApplication([
											('/', MainHandler),
											('/register',Register),
											('/login',Login),
											('/logout',Logout),
											('/account',Account),
											('/examples',Examples),
											('/calls', Calls),
											('/calls/(.*)',Call),
											('/caller-ids',CallerIds),
											('/caller-ids/(.*)',CallerId),
											('/phone-numbers',PhoneNumbers),
											('/phone-numbers/sms/(.*)',FakeSms),
											('/phone-numbers/voice/(.*)',FakeVoice),
											('/phone-numbers/twiml/(.*)',TwimlHandler),
											('/phone-numbers/(.*)',PhoneNumber),
											('/test',Test)
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
