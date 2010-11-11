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
from helpers import response, errors
from decorators import authorization
from models import conferences, participants, calls

class ConferenceInstance(base_handlers.InstanceHandler):
	def __init__(self):
		self.AllowedMethods = ['GET']
		self.InstanceModel = conferences.Conference.all()
		self.InstanceModelName = 'Conference'
		
class ConferenceList(base_handlers.ListHandler):
	def __init__(self):
		self.InstanceModel = messages.Message.all()
		self.AllowedMethods = ['GET']
		self.AllowedFilters = {
			'GET':[['Status','='],['FriendlyName','=']]#,['DateCreated','='],['DateUpdated', '=']]
		}
		self.ListName = 'Conferences'
		self.InstanceModelName = 'Conference'
		#Only for Put and Post
		self.AllowedProperties = {
		}


# http://www.twilio.com/docs/api/2010-04-01/rest/participant

# /2010-04-01/Accounts/{AccountSid}/Conferences/{ConferenceSid}/Participants/{CallSid}
class ParticipantInstance(base_handlers.InstanceHandler):
	def __init__(self):
		super(ParticipantInstance,self).__init__()
		self.AllowedMethods = ['GET']
		self.InstanceModel = participants.Participant.all()
		self.InstanceModelName = 'Participant'
		self.LastSidName = 'CallSid'
		#						 ['NAME =', location in args]
		self.AdditionalFilters = ['ConferenceSid =',0]
		self.AllowedProperties = { 'POST' : ['Muted'] }

	#Kick this participant from the conference. Returns HTTP 204 (No Content), with no body, if the participant was successfuly booted from the conference.
	@authorization.authorize_request
	def delete(self,API_VERSION,ACCOUNT_SID,*args):
		format = response.response_format( args[-1] )
		call = calls.Call.all().filter('AccountSid =',ACCOUNT_SID).filter('Sid =',)
		if call is not None:
			Valid = call.disconnect()
			if Valid:
				self.response.set_status(204)
			else:
				self.response.out.write(response.format_response(errors.rest_error_response(500,"Unable to disconnect call",format,12400,'http://www.twilio.com/docs/errors/12400'),format))
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(404,"The requested resource was not found",format),format))
class ParticipantList(base_handlers.ListHandler):
	def __init__(self):
		self.AllowedMethods = ['GET']
		self.InstanceModel = conferences.Conference.all()
		self.AdditionalFilters = ['ConferenceSid =',0]
		self.AllowedFilters = {
			'GET':[['Muted','=']]
		}

def main():
	application = webapp.WSGIApplication([
											('/(.*)/Accounts/(.*)/Conferences/(.*)/Participants/(.*)', ParticipantInstance),
											('/(.*)/Accounts/(.*)/Conferences/(.*)/Participants.*', ParticipantList),
											('/(.*)/Accounts/(.*)/Conferences/(.*)', ConferenceInstance)
											('/(.*)/Accounts/(.*)/Conferences.*', ConferenceList)
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
