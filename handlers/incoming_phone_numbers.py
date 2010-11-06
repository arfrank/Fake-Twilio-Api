# http://www.twilio.com/docs/api/2010-04-01/rest/incoming-phone-numbers

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
from google.appengine.ext import db
from random import randint

from helpers import response, parameters, xml
from handlers import base_handlers
from models import phone_numbers

from decorators import authorization

class IncomingPhoneNumberInstance(base_handlers.InstanceHandler):
	def __init__(self):
		self.ModelInstance = phone_numbers.Phone_Number.all()
		self.AllowedMethods = ['GET','POST','PUT','DELETE']

	@authorization.authorize_request
	def post(self,API_VERSION,ACCOUNT_SID, *args):
		IncomingPhoneNumberInstance.get(self,API_VERSION,ACCOUNT_SID,*args)	
	"""
	@authorization.authorize_request
	def delete(self,API_VERSION,ACCOUNT_SID, *args):
		format = response.response_format(args[0])
		PNSid = args[0].split('.')[0]
		phone_number = phone_numbers.Phone_Number.all().filter('Sid = ',PNSid).get()
		if phone_number is not None:
			db.delete(phone_number)
			self.response.set_status(204)
		else:
			self.error(400)
	"""
class IncomingPhoneNumberList(webapp.RequestHandler):
	@authorization.authorize_request
	def get(self, API_VERSION, ACCOUNT_SID, *args):
		#PAGING INFORMATION  will do this later
		pass

	@authorization.authorize_request
	def post(self,API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format(self.request.path.split('/')[-1])
		AreaCode = self.request.get('AreaCode',None)
		PhoneNumber = self.request.get('PhoneNumber',None)
		if (AreaCode is not None or AreaCode is not None) and not (AreaCode is not None and PhoneNumber is not None):
			#assume phone number is valid no matter what for now
			if (AreaCode is not None and len( AreaCode ) == 3) or (PhoneNumber is not None and len( PhoneNumber ) == 12 ):
				if AreaCode is not None and len( AreaCode ) == 3:
					phone_number = '+1'+str(AreaCode)+''.join(str(randint(0,9)) for i in range(7))
				elif PhoneNumber is not None and (len( PhoneNumber ) == 12:
					phone_number = PhoneNumber
				METHOD_TYPES = ['GET','POST']
				Phone_Number = phone_numbers.Phone_Number.new(
					FriendFriendlyName = self.request.get('FriendlyName',None)
					AccountSid = ACCOUNT_SID,
					PhoneNumber = phone_number,
					VoiceCallerIdLookup = self.request.get('VoiceCallerIdLookup',None)
					VoiceUrl = self.request.get('VoiceUrl',None)
					VoiceMethod = parameters.methods('VoiceMethod',self.request)
					VoiceFallbackUrl = self.request.get('VoiceFallbackUrl',None)
					VoiceFallbackMethod = parameters.methods('VoiceFallbackMethod',self.request)
					StatusCallback = self.request.get('StatusCallback',None)
					StatusCallbackMethod = parameters.methods('StatusCallbackMethod',self.request)
					SmsUrl = self.request.get('SmsUrl',None)
					SmsMethod = parameters.methods('SmsMethod',self.request)
					SmsFallbackUrl = self.request.get('SmsFallbackUrl',None)
					SmsFallbackMethod = parameters.methods('SmsFallbackMethod',self.request)
				)
				Phone_Number.put()
				response_data = Phone_Number.get_dict()
				if format == 'XML' or format == 'HTML':
					response_data = xml.add_nodes(response_data,'IncomingPhoneNumber')
				self.response.out.write(response.format_response(response_data,format))
			else:
				self.error(400)
		else:
			self.error(400)

	def put(self):
		self.error(404)
	def delete(self):
		self.error(404)

def main():
	application = webapp.WSGIApplication([
										('/(.*)/Accounts/(.*)/IncomingPhoneNumbers/(.*)', IncomingPhoneNumberInstance),
										('/(.*)/Accounts/(.*)/IncomingPhoneNumbers', IncomingPhoneNumberList),
										('/(.*)/Accounts/(.*)/IncomingPhoneNumbers.json', IncomingPhoneNumberList)

										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
