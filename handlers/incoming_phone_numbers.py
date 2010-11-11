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

from helpers import response, parameters, xml, errors
from handlers import base_handlers
from models import phone_numbers

from decorators import authorization

class IncomingPhoneNumberInstance(base_handlers.InstanceHandler):
	def __init__(self):
		super(IncomingPhoneNumberInstance,self).__init__()
		self.InstanceModel = phone_numbers.Phone_Number.all()
		self.AllowedMethods = ['GET','POST','PUT','DELETE']
		self.InstanceModelName = 'IncomingPhoneNumber'
		self.AllowedProperties = {
			'POST' : ['FriendlyName','ApiVersion','VoiceUrl','VoiceMethod','VoiceFallbackUrl','VoiceFallbackMethod','StatusCallback','StatusCallbackMethod','SmsUrl','SmsMethod','SmsFallbackUrl','SmsFallbackMethod','VoiceCallerIdLookup'],
			'PUT' : ['FriendlyName','ApiVersion','VoiceUrl','VoiceMethod','VoiceFallbackUrl','VoiceFallbackMethod','StatusCallback','StatusCallbackMethod','SmsUrl','SmsMethod','SmsFallbackUrl','SmsFallbackMethod','VoiceCallerIdLookup']
		}

class IncomingPhoneNumberList(base_handlers.ListHandler):
	def __init__(self):
		self.InstanceModel = phone_numbers.Phone_Number.all()
		self.AllowedMethods = ['GET']
		self.AllowedFilters = {
			'GET':[['To','='],['From','=']]#,['DateSent','=']] #DateSent will require some additional work
		}
		self.ListName = 'IncomingPhoneNumbers'
		self.InstanceModelName = 'IncomingPhoneNumber'

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
				elif PhoneNumber is not None and (len( PhoneNumber ) == 12):
					phone_number = PhoneNumber
				METHOD_TYPES = ['GET','POST']
				Phone_Number,Valid, TwilioCode,TwilioMsg = phone_numbers.Phone_Number.new(
					request = self.request,
					FriendlyName = self.request.get('FriendlyName',None),
					AccountSid = ACCOUNT_SID,
					PhoneNumber = phone_number,
					VoiceCallerIdLookup = self.request.get('VoiceCallerIdLookup',None),
					VoiceUrl = self.request.get('VoiceUrl',None),
					VoiceMethod = parameters.methods('VoiceMethod',self.request),
					VoiceFallbackUrl = self.request.get('VoiceFallbackUrl',None),
					VoiceFallbackMethod = parameters.methods('VoiceFallbackMethod',self.request),
					StatusCallback = self.request.get('StatusCallback',None),
					StatusCallbackMethod = parameters.methods('StatusCallbackMethod',self.request),
					SmsUrl = self.request.get('SmsUrl',None),
					SmsMethod = parameters.methods('SmsMethod',self.request),
					SmsFallbackUrl = self.request.get('SmsFallbackUrl',None),
					SmsFallbackMethod = parameters.methods('SmsFallbackMethod',self.request)
				)
				if Valid:
					Phone_Number.put()
					response_data = Phone_Number.get_dict()
					self.response.out.write(response.format_response(response.add_nodes(self,response_data,format),format))
				else:
					self.response.out.write(response.format_response(errors.rest_error_response(400,"Incorrect Parameters",format,TwilioCode,TwilioMsg),format))
					
			else:
				self.response.out.write(response.format_response(errors.rest_error_response(400,"Missing Parameters",format),format))
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(400,"Missing Parameters",format),format))

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
