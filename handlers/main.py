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
from google.appengine.ext.webapp import template
import os

import urllib
from libraries.gaesessions import get_current_session
from models import accounts,phone_numbers
from helpers import application

from decorators import webapp_decorator

class MainHandler(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), '../templates/home.html')
		self.response.out.write(template.render(path,{}))

class Register(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), '../templates/register.html')
		self.response.out.write(template.render(path,{}))

	def post(self):
		from hashlib import sha256
		required = ['email','password','password_confirm']
		if application.required(required,self.request) and self.request.get('password') == self.request.get('password_confirm'):
			exist_account = accounts.Account.get_by_key_name(self.request.get('email'))
			if exist_account is None:
				account = accounts.Account.new(key_name = self.request.get('email').lower(), email=self.request.get('email').lower(),password=self.request.get('password'))
				account.put()
				session = get_current_session()
				session.regenerate_id()
				session['Account'] = account
				self.redirect('/account')
			else:
				Register.get(self)
		else:
			Register.get(self)
		

class Login(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), '../templates/login.html')
		self.response.out.write(template.render(path,{}))

	def post(self):
		required = ['email','password']
		if application.required(required,self.request):
			Account = accounts.Account.get_by_key_name(self.request.get('email'))
			if Account is not None and Account.check_password(self.request.get('password')):
				session = get_current_session()
				session.regenerate_id()
				session['Account'] = Account
				self.redirect('/account')
			else:
				Login.get(self)

class Account(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self):
		path = os.path.join(os.path.dirname(__file__), '../templates/account.html')
		self.response.out.write(template.render(path,{'data':self.data}))

class PhoneNumbers(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self):
		self.data['PhoneNumbers'] = phone_numbers.Phone_Number.all().filter('AccountSid =',self.data['Account'].Sid)
		path = os.path.join(os.path.dirname(__file__), '../templates/phone-numbers.html')
		self.response.out.write(template.render(path,{'data':self.data}))

class PhoneNumber(webapp.RequestHandler):
	@webapp_decorator.check_logged_in
	def get(self,phone_number):
		phone_number = urllib.unquote(phone_number)
		self.data['PhoneNumber'] = phone_numbers.Phone_Number.all().filter('AccountSid = ',self.data['Account'].Sid).filter('PhoneNumber = ',phone_number).get()
		if self.data['PhoneNumber'] is not None:
			path = os.path.join(os.path.dirname(__file__), '../templates/phone-number.html')
			self.response.out.write(template.render(path,{'data':self.data}))
		else:
			self.redirect('/phone-numbers')

class Logout(webapp.RequestHandler):
	def get(self):
		session = get_current_session()
		session.terminate()
		self.redirect('/')
def main():
	application = webapp.WSGIApplication([
											('/', MainHandler),
											('/register',Register),
											('/login',Login),
											('/logout',Logout),
											('/account',Account),
											('/phone-numbers',PhoneNumbers),
											('/phone-numbers/(.*)',PhoneNumber)
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
