import unittest
import logging

from google.appengine.ext import db

import models

class IncomingPhoneNumberModel(unittest.TestCase):
	def setUp(self):
		#create account
		self.Account  = models.accounts.Account.new(key_name='email@email.com',email='email@email.com',password='password')
		self.Account.put()
		self.PhoneNumber = '+12405553456'

	def test_Incoming_Phone_Number_Creation_Success(self):
		Incoming_Phone_Number, Valid, TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new( request = None, AccountSid = self.Account.Sid, PhoneNumber = self.PhoneNumber, FriendlyName = 'Successful FriendlyName', VoiceUrl = 'http://www.twilio.com/', VoiceMethod = 'POST', VoiceFallbackUrl = 'http://www.twilio.com', VoiceFallbackMethod = 'POST', StatusCallback = 'http://www.twilio.com', StatusCallbackMethod = 'POST', SmsUrl = 'http://www.twilio.com', SmsFallback = 'POST', SmsFallbackUrl = 'http://www.twilio.com', SmsFallbackMethod = 'POST')
		self.assertTrue(Valid)
		Incoming_Phone_Number, Valid, TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new( request = None, AccountSid = self.Account.Sid, PhoneNumber = self.PhoneNumber, FriendlyName = 'Successful FriendlyName', VoiceUrl = 'http://www.twilio.com/', VoiceMethod = 'GET', VoiceFallbackUrl = 'http://www.twilio.com', VoiceFallbackMethod = 'GET', StatusCallback = 'http://www.twilio.com', StatusCallbackMethod = 'GET', SmsUrl = 'http://www.twilio.com', SmsFallback = 'GET', SmsFallbackUrl = 'http://www.twilio.com', SmsFallbackMethod = 'GET')
		self.assertTrue(Valid)

	def test_Incoming_Phone_Number_Creation_Failure_FriendlyName_Blank(self):
		Incoming_Phone_Number, Valid, TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new( request = None, AccountSid = self.Account.Sid, PhoneNumber = self.PhoneNumber, FriendlyName = '')
		self.assertFalse(Valid)
		self.assertEqual(20002, TwilioCode)
		
	def test_Incoming_Phone_Number_Creation_Failure_FriendlyName_TooLong(self):
		Incoming_Phone_Number, Valid, TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new( request = None, AccountSid = self.Account.Sid, PhoneNumber = self.PhoneNumber, FriendlyName = 'TOO LONGTOO LONGTOO LONGTOO LONGTOO LONGTOO LONGTOO LONGTOO LONGTOO LONGTOO LONGTOO LONGTOO LONGTOO LONG')
		self.assertFalse(Valid)
		self.assertEqual(20002, TwilioCode)
		
	def test_Incoming_Phone_Number_Creation_Failure_VoiceUrl(self):
		Incoming_Phone_Number, Valid, TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new( request = None, AccountSid = self.Account.Sid, PhoneNumber = self.PhoneNumber, FriendlyName = 'Successful FriendlyName', VoiceUrl = 'BADURL', VoiceMethod = 'POST', VoiceFallbackUrl = 'http://www.twilio.com', VoiceFallbackMethod = 'POST', StatusCallback = 'http://www.twilio.com', StatusCallbackMethod = 'POST', SmsUrl = 'http://www.twilio.com', SmsFallback = 'POST', SmsFallbackUrl = 'http://www.twilio.com', SmsFallbackMethod = 'POST')
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 21502)

	def test_Incoming_Phone_Number_Creation_Failure_VoiceMethod(self):
		Incoming_Phone_Number, Valid, TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new( request = None, AccountSid = self.Account.Sid, PhoneNumber = self.PhoneNumber, FriendlyName = 'Successful FriendlyName', VoiceUrl = 'http://www.twilio.com', VoiceMethod = 'paste', VoiceFallbackUrl = 'http://www.twilio.com', VoiceFallbackMethod = 'POST', StatusCallback = 'http://www.twilio.com', StatusCallbackMethod = 'POST', SmsUrl = 'http://www.twilio.com', SmsFallback = 'POST', SmsFallbackUrl = 'http://www.twilio.com', SmsFallbackMethod = 'POST')
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 21403)


	def test_Incoming_Phone_Number_Creation_Failure_VoiceFallbackUrl_Bad(self):
		Incoming_Phone_Number, Valid, TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new( request = None, AccountSid = self.Account.Sid, PhoneNumber = self.PhoneNumber, FriendlyName = 'Successful FriendlyName', VoiceUrl = 'http://www.twilio.com', VoiceMethod = 'POST', VoiceFallbackUrl = 'BAD URL', VoiceFallbackMethod = 'POST', StatusCallback = 'http://www.twilio.com', StatusCallbackMethod = 'POST', SmsUrl = 'http://www.twilio.com', SmsFallback = 'POST', SmsFallbackUrl = 'http://www.twilio.com', SmsFallbackMethod = 'POST')
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 21502)

	def test_Incoming_Phone_Number_Creation_Failure_VoiceFallbackUrl_NoStandardUrl(self):
		Incoming_Phone_Number, Valid, TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new( request = None, AccountSid = self.Account.Sid, PhoneNumber = self.PhoneNumber, FriendlyName = 'Successful FriendlyName', VoiceUrl = '', VoiceMethod = 'POST', VoiceFallbackUrl = 'BAD URL', VoiceFallbackMethod = 'POST', StatusCallback = 'http://www.twilio.com', StatusCallbackMethod = 'POST', SmsUrl = 'http://www.twilio.com', SmsFallback = 'POST', SmsFallbackUrl = 'http://www.twilio.com', SmsFallbackMethod = 'POST')
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 21502)


	def test_Incoming_Phone_Number_Creation_Failure_VoiceFallbackMethod(self):
		Incoming_Phone_Number, Valid, TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new( request = None, AccountSid = self.Account.Sid, PhoneNumber = self.PhoneNumber, FriendlyName = 'Successful FriendlyName', VoiceUrl = 'http://www.twilio.com', VoiceMethod = 'POST', VoiceFallbackUrl = 'http://www.twilio.com', VoiceFallbackMethod = 'paste', StatusCallback = 'http://www.twilio.com', StatusCallbackMethod = 'POST', SmsUrl = 'http://www.twilio.com', SmsFallback = 'POST', SmsFallbackUrl = 'http://www.twilio.com', SmsFallbackMethod = 'POST')
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 21403)

