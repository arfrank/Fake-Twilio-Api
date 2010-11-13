# http://www.twilio.com/docs/api/2010-04-01/rest/outgoing-caller-ids
# /2010-04-01/Accounts/{AccountSid}/OutgoingCallerIds/{OutgoingCallerIdSid}

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

from handlers import base_handlers

from models import phone_numbers, outgoing_caller_ids

from decorators import authorization

class OutgoingCallerIdInstance(base_handlers.InstanceHandler):
	def __init__(self):
		super(OutgoingCallerId,self).__init__()
		self.AllowedMethods = ['GET','PUT','POST','DELETE']
		self.AllowedProperties = {
			'POST':['FriendlyName'],
			'PUT': ['FriendlyName']
		}
		self.InstanceModel = outgoing_caller_ids.Outgoing_Caller_Id.all()
		
class OutgoingCallerIdList(base_handlers.ListHandler):
	def __init__(self):
		super(OutgoingCallerId,self).__init__()
		self.AllowedMethods = ['GET','POST']
		self.AllowedFilters = {
			'GET':[['PhoneNumber','='],['FriendlyName','=']]
		}
		self.ListName = 'OutgoingCallerIds'
		self.InstanceModelName = 'OutgoingCallerId'
		#Only for Put and Post
		self.InstanceModel = outgoing_caller_ids.Outgoing_Caller_Id.all()
	
	@authorization.authorize_request
	def post(self,API_VERSION,ACCOUNT_SID,*args):
		"""
		Adds a new CallerID to your account. After making this request, Twilio will return to you a validation code and Twilio will dial the phone number given to perform validation. The code returned must be entered via the phone before the CallerID will be added to your account. The following parameters are accepted:

		Required Parameters

		Parameter	Description
		PhoneNumber	The phone number to verify. Should be formatted with a '+' and country code e.g., +16175551212 (E.164 format). Twilio will also accept unformatted US numbers e.g., (415) 555-1212, 415-555-1212.
		Optional Parameters

		Parameter	Description
		FriendlyName	A human readable description for the new caller ID with maximum length 64 characters. Defaults to a nicely formatted version of the number.
		CallDelay	The number of seconds, between 0 and 60, to delay before initiating the validation call. Defaults to 0.
		This will create a new CallerID validation request within Twilio, which initiates a call to the phone number provided and listens for a validation code. The validation request is represented in the response by the following properties:

		Response Properties

		Property	Description
		AccountSid	The unique id of the Account to which the Validation Request belongs.
		PhoneNumber	The incoming phone number being validated, formatted with a '+' and country code e.g., +16175551212 (E.164 format).
		FriendlyName	The friendly name you provided, if any.
		ValidationCode	The 6 digit validation code that must be entered via the phone to validate this phone number for Caller ID.
		"""

		pass

def main():
	application = webapp.WSGIApplication([
											('/(.*)/Accounts/(.*)/OutgoingCallerIds/(.*)', OutgoingCallerId),
											('/(.*)/Accounts/(.*)/OutgoingCallerIds.*', OutgoingCallerId),
											
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()