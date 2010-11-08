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
from helpers import response, parameters, sid, authorization, errors
from decorators import authorization
from models import accounts,messages

class MessageList(base_handlers.ListHandler):
	def __init__(self):
		self.InstanceModel = messages.Message.all()
		self.AllowedMethods = ['GET']
		self.AllowedFilters = {
			'GET':[['To','='],['From','='],['DateSent','=']]
		}
		self.ListName = 'SmsMessages'
		self.InstanceModelName = 'SmsMessage'
		#Only for Put and Post
		self.AllowedProperties = {
		}

#OVERLOAD THE post method to a local version cause thats going to be necessary for each one		
	@authorization.authorize_request
	def post(self, API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format(self.request.path.split('/')[-1])
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
			response_data = Message.get_dict()
			self.response.out.write(response.format_response(response.add_nodes(self,response_data,format),format))
			Message.put()
			#DO SOME THINGS DEPENDING ON ACCOUNT SETTINGS
			#DEFAULT WILL BE TO SEND MESSAGE, CHARGE FOR IT AND UPDATE WHEN SENT
			Message.send()
			#make sure put happens before callback happens
			if Message.StatusCallback is not None:
				taskqueue.Queue('StatusCallbacks').add(taskqueue.Task(url='/Callbacks/SMS', params = {'SmsSid':Message.Sid}))
		else:
			#This should either specify a twilio code either 21603 or 21604
			self.response.out.write(response.format_response(errors.rest_error_response(400,"Missing Parameters",format),format))

		
class MessageInstanceResource(base_handlers.InstanceHandler):
	def __init__(self):
		self.InstanceModel = messages.Message.all()
		self.AllowedMethods = ['GET']
		self.InstanceModelName = 'SmsMessage'
		
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
