import unittest

import logging

from decorators import authorization
import models

from google.appengine.ext import db

class AuthorizationDecorator(unittest.TestCase):
	def setUp(self):
		self.Account  = models.accounts.Account.new(key_name='email@email.com',email='email@email.com',password='password')
		self.Account.put()
		
	def test_Authorization_Success(self):
		def blank(self):
			pass
		authorized_method = authorization.authorize_request(blank(self))
		logging.info( authorized_method )
		# need to fake a web request
		# authorized_method(self, '2010-04-01',self.Account.Sid,{})