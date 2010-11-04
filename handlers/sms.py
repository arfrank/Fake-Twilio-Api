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
from helpers import response,parameters,sid
import random
import string
class MessageList(webapp.RequestHandler):
	def get(self, API_VERSION, ACCOUNT_SID, *args):
		MessageList.post(self,API_VERSION,ACCOUNT_SID)
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

	def post(self, API_VERSION, ACCOUNT_SID, *args):
		if parameters.required(['From','To','Body'],self.request):
			import datetime
			#time is hardcoded -8 hours from UTC, will fix this later with other date things abstracted away
			now_time = datetime.datetime.now()+datetime.timedelta(hours=-8)
			now_formatted = now_time.strftime('%a, %d %b %Y %H:%M:%S %z')
			response_data = {
			    "account_sid": ACCOUNT_SID, 
			    "api_version": API_VERSION, 
			    "body": self.request.get('Body'), 
			    "date_created": now_formatted, 
			    "date_sent": None, 
			    "date_updated": now_formatted, 
			    "direction": "outbound-api", 
			    "from": self.request.get('From'), 
			    "price": None, 
			    "status": "queued", 
			    "to": self.request.get('To'), 
			    "uri": self.request.path			
			}
			SMSSid = 'SM'+ sid.compute_sid(response_data)
			response_data['sid'] = SMSSid
			if self.request.get('StatusCallback',None) is not None:
				response_data['StatusCallback'] = self.request.get('StatusCallback')
			format = 'JSON'
			self.response.out.write(response.format_response(response_data,format))
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
	def get(self,API_VERSION,ACCOUNT_SID, *args):
		SMSMessageSid = args[0]
		format = response.response_format(SMSMessageSid)
		data = {
		'Sid':'',
		'DateCreated':'',
		'DateUpdated':'',
		'DateSent':'',
		'AccountSid':ACCOUNT_SID,
		'From':'',
		'To':'',
		'Body':'',
		'Status':'',
		'Direction':'',
		'Price':'',
		'ApiVersion':API_VERSION,
		'Uri':self.request.path
		}
		if format == 'XML':
			data = {
					'TwilioResponse':
						{
						'SMSMessage':data
						}
					}
		self.response.out.write(response.format_response(data,format))

	def post(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)
		
	def put(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)

	def delete(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)
		
def main():
	application = webapp.WSGIApplication([
											('/(.*)/accounts/(.*)/SMS/Messages', MessageList),
											('/(.*)/accounts/(.*)/SMS/Messages.json', MessageList),
											('/(.*)/accounts/(.*)/SMS/Messages/(.*)', MessageInstanceResource)
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
