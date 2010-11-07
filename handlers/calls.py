# /2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}
# /2010-04-01/Accounts/{AccountSid}/Calls


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

from helpers import parameters,response,errors

from decorators import authorization
from models import calls

class CallInstance(base_handlers.InstanceHandler):
	def __init__(self):
		self.AllowedMethods = ['GET']
		self.ModelInstance = calls.Call.all()

# Initiates a call redirect or terminates a call. See Modifying Live Calls for details.
	def post(self):
		pass

# Represents a list of recordings generated during the call identified by {CallSid}. See the Recordings section for resource properties and response formats.
class CallInstanceRecordings(base_handlers.InstanceHandler):
	def __init__(self):
		self.AllowedMethods = ['GET']
		self.ModelInstance = calls.Call.all()

# Represents a list of notifications generated during the call identified by {CallSid}. See the Notifications section for resource properties and response formats.
class CallInstanceNotifications(base_handlers.InstanceHandler):
	def __init__(self):
		self.AllowedMethods = ['GET']
		self.ModelInstance = calls.Call.all()

# GET gets a list of calls
# POST initiates a new call
class CallList(base_handlers.ListHandler):
	def __init__(self):
		"""
		To	Only show calls to this phone number.
		From	Only show calls from this phone number.
		Status	Only show calls currently in this status. May be queued, ringing, in-progress, completed, failed, busy, or no-answer.
		StartTime	Only show calls that started on this date, given as YYYY-MM-DD. Also supports inequalities, such as StartTime<=YYYY-MM-DD for calls that started at or before midnight on a date, and StartTime>=YYYY-MM-DD for calls that started at or after midnight on a date.
		EndTime	Only show calls that ended on this date, given as YYYY-MM-DD. Also supports inequalities, such as EndTime<=YYYY-MM-DD for calls that ended at or before midnight on a date, and EndTime>=YYYY-MM-DD for calls that end at or after midnight on a date.
		"""
		self.ModelInstance = calls.Call.all()
		self.AllowedMethods = ['GET']
		self.AllowedFilters = {
			'GET':[['To','='],['From','='],['Status','='],['StartTime','='],['EndTime','=']]
		}
		self.ListName = 'Calls'
		self.InstanceModelName = 'Call'
	
	@authorization.authorize_request
	def post(self,API_VERSION,ACCOUNT_SID,*args):
		"""
		From	The phone number to use as the caller id. Format with a '+' and country code e.g., +16175551212 (E.164 format). Must be a Twilio number or a valid outgoing caller id for your account.
		To	The number to call formatted with a '+' and country code e.g., +16175551212 (E.164 format). Twilio will also accept unformatted US numbers e.g., (415) 555-1212, 415-555-1212.
		Url	The fully qualified URL that should be consulted when the call connects. Just like when you set a URL for your inbound calls.

		Method	The HTTP method Twilio should use when requesting the required Url parameter's value above. Defaults to POST.
		FallbackUrl	A URL that Twilio will request if an error occurs requesting or executing the TwiML at Url.
		FallbackMethod	The HTTP method that Twilio should use to request the FallbackUrl. Must be either GET or POST. Defaults to POST.
		StatusCallback	A URL that Twilio will request when the call ends to notify your app.
		StatusCallbackMethod	The HTTP method Twilio should use when requesting the above URL. Defaults to POST.
		SendDigits	A string of keys to dial after connecting to the number. Valid digits in the string include: any digit (0-9), '#' and '*'. For example, if you connected to a company phone number, and wanted to dial extension 1234 and then the pound key, use SendDigits=1234#. Remember to URL-encode this string, since the '#' character has special meaning in a URL.
		IfMachine	Tell Twilio to try and determine if a machine (like voicemail) or a human has answered the call. Possible values are Continue and Hangup. See the answering machines section below for more info.
		Timeout	The integer number of seconds that Twilio should allow the phone to ring before assuming there is no answer. Default is 60 seconds, the maximum is 999 seconds. Note, you could set this to a low value, such as 15, to hangup before reaching an answering machine or voicemail. Also see the answering machine section for other solutions.
		"""
		format = response.response_format(self.request.path.split('/')[-1])
		if parameters.required(['From','To','Url'],self.request):
			Call = calls.Call.new()
			Call.put()
			if self.request.get('StatusCallback',None) is not None:
				method = self.request.get('StatusCallbackMethod','POST').upper()
				if method not in ['GET','POST']:
					method = 'POST'
				taskqueue.Queue('StatusCallbacks').add(taskqueue.Task(url='/Callbacks/Call', method = method, params = {'CallSid':Call.Sid}))
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(400,"Missing Parameters",format),format))
			
def main():
	application = webapp.WSGIApplication([
									('/(.*)/Accounts/(.*)/Calls/(.*)/Recordings', CallInstanceRecordings),
									('/(.*)/Accounts/(.*)/Calls/(.*)/Notifications', CallInstanceNotifications),
									('/(.*)/Accounts/(.*)/Calls/(.*)', CallInstance),
									('/(.*)/Accounts/(.*)/Calls', CallList)
									],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
