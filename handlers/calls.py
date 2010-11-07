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

from handlers import base_handlers

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
class CallList(webapp.RequestHandler):
	def get(self):
		pass

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
