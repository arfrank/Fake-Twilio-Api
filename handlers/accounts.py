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
from models import accounts

class Accounts(base_handlers.InstanceHandler):
	def __init__(self):
		super(Accounts,self).__init__()
		self.AllowedMethods = ['GET','PUT','POST']
		self.InstanceModel = accounts.Account.all()
		self.InstanceModelName = 'Account'
		self.AllowedProperties = {
			'POST' : ['FriendlyName'],
			'PUT' : ['FriendlyName']
		}

def main():
	application = webapp.WSGIApplication([
										('/(.*)/Accounts/(.*)', Accounts)
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
