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

from models import notifications

# /2010-04-01/Accounts/{AccountSid}/Transcriptions/{TranscriptionSid}
class NotificationInstance(base_handlers.InstanceHandler):
	def __init__(self):
		self.AllowedMethods = ['GET','DELETE']
		self.ModelInstance = notifications.Notification.all()

class NotificationList(base_handlers.ListHandler):
	def __init__(self):
		self.AllowedMethods = ['GET']
		self.ModelInstance = notifications.Notification.all()


def main():
	application = webapp.WSGIApplication([
											('/(.*)/Accounts/(.*)/Notifications/(.*)', NotificationsInstance),
											('/(.*)/Accounts/(.*)/Notifications', NotificationsList)
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
