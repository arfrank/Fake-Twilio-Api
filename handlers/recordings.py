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
	def get(self, API_VERSION, *args):
		self.response.out.write('Hello world!'+args[0])

class RecordingInstanceTranscription(base_handlers.InstanceHandler):
	def __init__(self):
		self.InstanceModel = recordings.Recording.all()
		self.AllowedMethods = ['GET','DELETE']

class RecordingList(webapp.RequestHandler):
	def __init__(self):
		self.InstanceModel = recordings.Recording.all()
		self.AllowedMethods = ['GET']
		
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
