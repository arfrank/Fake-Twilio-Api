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
from google.appengine.api.labs import taskqueue

from helpers import response,parameters,sid,authorization
from decorators import authorization
import random
import string

from models import accounts,messages

class MessageList(webapp.RequestHandler):
#	@authorization.authorize_request
	def get(self, API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format(self.request.path.split('/')[-1])
		Messages = messages.Message.all()
		if self.request.get('To',None) is not None:
			Messages.filter('To = ',self.request.get('To'))
		if self.request.get('From',None) is not None:
			Messages.filter('From = ',self.request.get('From'))
		if self.request.get('DateSent',None) is not None:
			pass
			#To be implimented later
		#This should be put into a helper or something to automatically populate,
		#or be a subclass of a list handler and just do Messagy things for messages
		Page = 0
		PageSize = 50
		if self.request.get('Page',None) is not None:
			try:
				Page = int(self.request.get('Page'))
			except Exception, e:
				Page = 0
		if Page < 0:
			Page = 0
		if self.request.get('PageSize',None) is not None:
			try:
				PageSize = int(self.request.get('PageSize'))
			except Exception, e:
				PageSize = 50
		if PageSize > 1000:
			PageSize = 1000
		if PageSize < 0:
			PageSize = 1
		smsCount = Messages.count()
		SmsMessages = Messages.fetch(PageSize,(Page*PageSize))
		response_data = {
						"start":(Page*PageSize),
						"total":smsCount,
						'SmsMessages':[]
						}
		for sms in Message:
			response_data['SmsMessages'].append(sms)
		self.response.out.write(response.format_response(response_data,format))
		pass
	"""
	{
	    "account_sid": "AC5ef872f6da5a21de157d80997a64bd33", 
	    "api_version": "2010-04-01", 
	    "body": "Jenny please?! I love you <3", 
	    "date_created": "Wed, 18 Aug 2010 20:01:40 +0000", 
	    "date_sent": null, 
	    "date_updated": "Wed, 18 Aug 2010 20:01:40 +0000", 
	    "direction": "outbound-api", 
	    "from": "+14158141829", 
	    "price": null, 
	    "sid": "SM90c6fc909d8504d45ecdb3a3d5b3556e", 
	    "status": "queued", 
	    "to": "+14159352345", 
	    "uri": "/2010-04-01/Accounts/AC5ef872f6da5a21de157d80997a64bd33/SMS/Messages/SM90c6fc909d8504d45ecdb3a3d5b3556e.json"
	}
	"""

	@authorization.authorize_request
	def post(self, API_VERSION, ACCOUNT_SID, *args):
		if parameters.required(['From','To','Body'],self.request):
			Message = messages.Message.new(
										To = self.request.get('To'),
										From = self.request.get('From'),
										Body = self.request.get('Body'),
										AccountSid = ACCOUNT_SID,
										Direction = 'outbound-api',
										Status = 'queued'
									)
			if self.request.get('StatusCallback',None) is not None:
				Message.StatusCallback = self.request.get('StatusCallback')

			format = response.response_format(self.request.path.split('/')[-1])

			response_data = Message.get_dict()
			if format == 'XML':
				response_data = {
						'TwilioResponse':
							{
							'SMSMessage':response_data
							}
						}
			self.response.out.write(response.format_response(response_data,format))
			Message.put()
			#make sure put happens before callback happens
			if Message.StatusCallback is not None:
				taskqueue.Queue('StatusCallbacks').add(taskqueue.Task(url='/Callbacks/SMS', params = {'SmsSid':Message.Sid}))
		else:
			self.error(400)

	def put(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)
	def delete(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)
		
class MessageInstanceResource(webapp.RequestHandler):
	"""
	Sid	A 34 character string that uniquely identifies this resource.
	DateCreated	The date that this resource was created, given in RFC 2822 format.
	DateUpdated	The date that this resource was last updated, given in RFC 2822 format.
	DateSent	The date that the SMS was sent, given in RFC 2822 format.
	AccountSid	The unique id of the Account that sent this SMS message.
	From	The phone number that initiated the message in E.164 format. For incoming messages, this will be the remote phone. For outgoing messages, this will be one of your Twilio phone numbers.
	To	The phone number that received the message in E.164 format. For incoming messages, this will be one of your Twilio phone numbers. For outgoing messages, this will be the remote phone.
	Body	The text body of the SMS message. Up to 160 characters long.
	Status	The status of this SMS message. Either queued, sending, sent, or failed.
	Direction	The direction of this SMS message. incoming for incoming messages, outbound-api for messages initiated via the REST API, outbound-call for messages initiated during a call or outbound-reply for messages initiated in response to an incoming SMS.
	Price	The amount billed for the message.
	ApiVersion	The version of the Twilio API used to process the SMS message.
	Uri	The URI for this resource, relative to https://api.twilio.com
	"""
	@authorization.authorize_request
	def get(self,API_VERSION,ACCOUNT_SID, *args):
		SMSMessageSid = args[0]
		format = response.response_format(SMSMessageSid)
		SMSMessageSid = args[0].split('.')[0]
		Message = messages.Message.all().filter('Sid =',SMSMessageSid).get()
		if Message is not None and True or Message.AccountSid == ACCOUNT_SID:
			response_data = Message.get_dict()
			response_data['ApiVersion'] = API_VERSION
			response_data['Uri'] = self.request.path
			if format == 'XML':
				response_data = {
						'TwilioResponse':
							{
							'SMSMessage':response_data
							}
						}
			self.response.out.write(response.format_response(response_data,format))
		else:
			self.error(400)

	def post(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)
		
	def put(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)

	def delete(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)
		
def main():
	application = webapp.WSGIApplication([
											('/(.*)/Accounts/(.*)/SMS/Messages', MessageList),
											('/(.*)/Accounts/(.*)/SMS/Messages.json', MessageList),
											('/(.*)/Accounts/(.*)/SMS/Messages/(.*)', MessageInstanceResource)
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
