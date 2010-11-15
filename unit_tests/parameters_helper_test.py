import unittest
import logging

from google.appengine.ext import db

from helpers import parameters

class ParametersParsePhoneNumbers(unittest.TestCase):
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
