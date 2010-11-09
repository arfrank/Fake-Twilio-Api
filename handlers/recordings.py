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

from decorators import authorization

from models import recordings
# /2010-04-01/Accounts/{AccountSid}/Recordings/{RecordingSid}.txt gets a trancription, will have to special case this.
# /2010-04-01/Accounts/{AccountSid}/Recordings/{RecordingSid}
class RecordingInstance(base_handlers.InstanceHandler):
	def __init__(self):
		self.InstanceModel = recordings.Recording.all()
		self.AllowedMethods = ['GET','DELETE']

#OVERRIDE THE DEFAULT BECAUSE THESE ARENT BLOCKED BY DEFAULT
#Actually exact same functionality, just not blocked, plus expanded feature set
	def get(self, API_VERSION, *args):		
		format = response.response_format( args[0] )
		InstanceSid = args[0].split('.')[0]
		Instance = self.InstanceModel.filter('Sid =',InstanceSid).filter('AccountSid = ',ACCOUNT_SID).get()
		if Instance is not None:
			response_data = Instance.get_dict()
			response_data['ApiVersion'] = API_VERSION
			response_data['Uri'] = self.request.path
			self.response.out.write(response.format_response(response.add_nodes(self,response_data,format),format))
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(404,"The requested resource was not found",format),format))

class RecordingInstanceTranscription(base_handlers.InstanceHandler):
	def __init__(self):
		self.InstanceModel = recordings.Recording.all()
		self.AllowedMethods = ['GET','DELETE']

class RecordingList(webapp.RequestHandler):
	def __init__(self):
		self.InstanceModel = recordings.Recording.all()
		self.AllowedMethods = ['GET']
		self.AllowedFilters = {
			'GET':[['CallSid','='],['DateCreated','=']
		}
		self.ListName = 'Recordings'
		self.InstanceModelName = 'Recordings'
		#Only for Put and Post
		self.AllowedProperties = {
		}

def main():
	application = webapp.WSGIApplication([
											('/(.*)/Accounts/(.*)/Recordings/(.*)/Transcriptions', Transcriptions),
											('/(.*)/Accounts/(.*)/Recordings/(.*)', RecordingInstance),
											('/(.*)/Accounts/(.*)/Recordings', RecordingList)
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
