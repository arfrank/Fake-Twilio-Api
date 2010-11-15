import unittest
import logging

from google.appengine.ext import db

import models

class CallModel(unittest.TestCase):
	def setUp(self):
		self.Account = models.accounts.Account.new(key_name = 'email@email.com', email="email@email.com", password="password")
		#account creation is actually done via the webapp, so don't have to think about creation		

	def test_Account_Password_Check_Success(self):
		PW = self.Account.check_password('password')
		self.assertTrue(PW)

	def test_Account_Password_Check_Failure(self):
		PW = self.Account.check_password('failure')
		self.assertFalse(PW)
		
	def test_Account_FriendlyName_Validation_None(self):
		Valid, TwilioCode, TwilioMsg = self.Account.validate(None, 'FriendlyName', '')
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 20002)
		
	def test_Account_FriendlyName_Validation_Success(self):
		Valid, TwilioCode, TwilioMsg = self.Account.validate(None, 'FriendlyName', 'This is an okay length friendly name')
		self.assertTrue(Valid)
		self.assertEqual(TwilioCode, 0)
		
	def test_Account_FriendlyName_Validation_TooLong(self):
		Valid, TwilioCode, TwilioMsg = self.Account.validate(None, 'FriendlyName', 'TOO LONG OF A NAME TOO LONG OF A NAME TOO LONG OF A NAME TOO LONG OF A NAME TOO LONG OF A NAME TOO LONG OF A NAME TOO LONG OF A NAME')
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 20002)
		