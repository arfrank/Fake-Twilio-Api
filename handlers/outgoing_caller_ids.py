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

from models import phone_numbers

from decorators import authorization

class OutgoingCallerId(base_handlers.InstanceHandler):
	def __init__(self):
		self.AllowedMethods = ['GET','PUT','POST','DELETE']
		self.InstanceModel = phone_numbers.Phone_Number.all()
		

def main():
	application = webapp.WSGIApplication([('/(.*)/Accounts/(.*)/OutgoingCallerIds/(.*)', OutgoingCallerId)],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()