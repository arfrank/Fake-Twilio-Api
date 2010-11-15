import unittest
import logging

from google.appengine.ext import db

import models

from helpers import parameters

class Parameters_Parse_Phone_Numbers(unittest.TestCase):
	def setUp(self):
		self.ValidPhoneNumber = '+12405559999'
		self.TooShortPhoneNumber = '+1 222 222 222'
		self.BadPhoneNumber = '+1999a123a23abc32'
		
	def test_Parse_Phone_Number_Valid(self):
		phone_number, Valid = parameters.parse_phone_number(self.ValidPhoneNumber)
		self.assertTrue(Valid)
		self.assertEqual(phone_number, self.ValidPhoneNumber)
		
	def test_Parse_Phone_Number_Failure_TooShort(self):
		phone_number, Valid = parameters.parse_phone_number(self.TooShortPhoneNumber)
		self.assertFalse(Valid)

	def test_Parse_Phone_Number_Failure_BadNumber(self):
		phone_number, Valid = parameters.parse_phone_number(self.BadPhoneNumber)
		self.assertFalse(Valid)

class Parameters_Valid_To_Phone_Number(unittest.TestCase):
	def setUp(self):
		self.BadPhoneNumber = '+1999a123a23abc32'
		self.Account  = models.accounts.Account.new(key_name='email@email.com',email='email@email.com',password='password')
		self.Account.put()
		self.PhoneNumber,Valid,TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new(PhoneNumber = '+13015559999', request = None, AccountSid = self.Account.Sid)
		self.OutgoingCallerId, Valid, TwilioCode, TwilioMsg = models.outgoing_caller_ids.Outgoing_Caller_Id.new(PhoneNumber = '+13015556666', request = None, AccountSid = self.Account.Sid)
		db.put([self.PhoneNumber, self.OutgoingCallerId])
		
	def test_To_Phone_Number_Success(self):
		Valid, TwilioCode, TwilioMsg = parameters.valid_to_phone_number(self.PhoneNumber.PhoneNumber)
		self.assertTrue(Valid)

	def test_To_Phone_Number_Failure_Blank_Required(self):
		Valid, TwilioCode, TwilioMsg = parameters.valid_to_phone_number('',True)
		self.assertFalse(Valid)

	def test_To_Phone_Number_Failure_Bad_Number(self):
		Valid, TwilioCode, TwilioMsg = parameters.valid_to_phone_number(self.BadPhoneNumber,True)
		self.assertFalse(Valid)
		
class Parameters_Valid_From_Phone_Number(unittest.TestCase):
	def setUp(self):
		self.BadPhoneNumber = '+1999a123a23abc32'
		self.Account  = models.accounts.Account.new(key_name='email@email.com',email='email@email.com',password='password')
		self.Account.put()
		self.PhoneNumber,Valid,TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new(PhoneNumber = '+13015559999', request = None, AccountSid = self.Account.Sid)
		self.OutgoingCallerId, Valid, TwilioCode, TwilioMsg = models.outgoing_caller_ids.Outgoing_Caller_Id.new(PhoneNumber = '+13015556666', request = None, AccountSid = self.Account.Sid)
		db.put([self.PhoneNumber, self.OutgoingCallerId])