#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from helpers import authorization

from google.appengine.api import urlfetch

from hashlib import sha1
import urllib

from models import messages,accounts


class SMSCallback(webapp.RequestHandler):
	"""
	This is where we will update the user with a callback,  depending on what has happened also can force a failed message
	Lets get basic callback with current message status down
	
	Actually here will only ever be a callback, never the real information
	"""
	def post(self):
		SmsSid = self.request.get('SmsSid',None)
		if SmsSid is not None:
			Message = messages.Message.all().filter('Sid = ',SmsSid).get()
			if Message.StatusCallback is not None:
				payload = {
				'SmsSid':SmsSid,
				'SmsStatus':Message.Status
				}
				Account = accounts.Account.all().filter('Sid = ',Message.AccountSid).get()
				Twilio_Signature = authorization.create_twilio_authorization_hash(Account,Message.StatusCallback, payload)
				urlfetch.fetch(url = Message.StatusCallback,payload = urllib.urlencode(payload) ,method = urlfetch.POST, headers = {'X-Twilio-Signature':Twilio_Signature})

class CallCallback(webapp.RequestHandler):
	def post(self):
		pass

def main():
    application = webapp.WSGIApplication([
											('/Callbacks/SMS', SMSCallback)
											('/Callbacks/Call', CallCallback)
										],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
