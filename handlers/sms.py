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

from handlers import base_handlers
from helpers import response, parameters, sid, authorization, xml
from decorators import authorization
import random
import string

from models import accounts,messages

class MessageList(base_handlers.ListHandler):
	def __init__(self):
		self.ModelInstance = messages.Message.all()
		self.AllowedMethods = ['GET']
		self.AllowedFilters = {
			'GET':[['To','='],['From','='],['DateSent','=']]
		}
		self.ListName = 'SmsMessages'
		self.ListModelName = 'SmsMessage'
		
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
			if format == 'XML' or format == 'HTML':
				response_data = xml.add_nodes(response_data,'SMSMessage')
			self.response.out.write(response.format_response(response_data,format))
			Message.put()
			#make sure put happens before callback happens
			if Message.StatusCallback is not None:
				taskqueue.Queue('StatusCallbacks').add(taskqueue.Task(url='/Callbacks/SMS', params = {'SmsSid':Message.Sid}))
		else:
			#This should either specify a twilio code either 21603 or 21604
			self.response.out.write(response.format_response(errors.rest_error_response(400,"Missing Parameters",format),format))

	@authorization.authorize_request
	def put(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)

	@authorization.authorize_request
	def delete(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)
		
class MessageInstanceResource(base_handlers.InstanceHandler):
	def __init__(self):
		self.ModelInstance = messages.Message.all()
		self.AllowedMethods = ['GET']
		
def main():
	application = webapp.WSGIApplication([
											('/(.*)/Accounts/(.*)/SMS/Messages/(.*)', MessageInstanceResource),
											('/(.*)/Accounts/(.*)/SMS/Messages', MessageList),
											('/(.*)/Accounts/(.*)/SMS/Messages.json', MessageList)
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
