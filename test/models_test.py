import unittest
import logging
from google.appengine.ext import db
import models

class MessagesModel(unittest.TestCase):
	def setUp(self):
		#create account
		self.Account  = models.accounts.Account.new(key_name='email@email.com',email='email@email.com',password='password')
		self.Account.put()
		self.PhoneNumber,Valid,TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new(PhoneNumber = '+13015559999', request = None, AccountSid = self.Account.Sid)
		self.PhoneNumber.put()
		self.FakeToNumber = '+12405551234'
		self.BodyText = 'Fake Body Text'
		self.LongBodyText = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor. Pellentesque auctor nisi id magna consequat sagittis. Curabitur dapibus enim sit amet elit pharetra tincidunt feugiat nisl imperdiet. Ut convallis libero in urna ultrices accumsan. Donec sed odio eros. Donec viverra mi quis quam pulvinar at malesuada arcu rhoncus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris vitae nisi at sem facilisis semper ac in est.'
		
	def test_Message_creation_success(self):
		Message, Valid, TwilioCode, TwilioMsg = models.messages.Message.new(To = self.FakeToNumber, From = self.PhoneNumber.PhoneNumber, Body = self.BodyText, Direction = 'outbound-api', request = None, AccountSid = self.Account.Sid)
		self.assertTrue(Valid)
		self.assertEqual(Message.To,self.FakeToNumber)
		self.assertEqual(Message.From,self.PhoneNumber.PhoneNumber)
		self.assertEqual(Message.Body,self.BodyText)

	def test_Message_creation_to_failure(self):
		Message, Valid, TwilioCode, TwilioMsg = models.messages.Message.new(To = 'adsfadsfasdf', From = self.PhoneNumber.PhoneNumber, Body = 'Good body text', Direction = 'outbound-api', request = None, AccountSid = self.Account.Sid)
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 21401)

	def test_Message_creation_from_failure_mistyped_number(self):
		Message, Valid, TwilioCode, TwilioMsg = models.messages.Message.new(To = self.FakeToNumber, From = '+240555a123', Body = 'Good body text', Direction = 'outbound-api', request = None, AccountSid = self.Account.Sid)
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 21401)

	def test_Message_creation_from_failure_not_allowed_number(self):
		Message, Valid, TwilioCode, TwilioMsg = models.messages.Message.new(To = self.FakeToNumber, From = '+5555555555', Body = 'Good body text', Direction = 'outbound-api', request = None, AccountSid = self.Account.Sid)
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 14108)

	def test_Message_creation_body_blank_failure(self):
		Message, Valid, TwilioCode, TwilioMsg = models.messages.Message.new(To = self.FakeToNumber, From = self.PhoneNumber.PhoneNumber, Body = '', Direction = 'outbound-api', request = None, AccountSid = self.Account.Sid)
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 14103)

	def test_Message_creation_body_long_failure(self):
		Message, Valid, TwilioCode, TwilioMsg = models.messages.Message.new(To = self.FakeToNumber, From = self.PhoneNumber.PhoneNumber, Body = self.LongBodyText, Direction = 'outbound-api', request = None, AccountSid = self.Account.Sid)
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 21605)

	def test_Message_creation_callback_failure(self):
		Message, Valid, TwilioCode, TwilioMsg = models.messages.Message.new(To =  self.FakeToNumber, From = self.PhoneNumber.PhoneNumber, Body = 'Good body text', Direction = 'outbound-api', request = None, AccountSid = self.Account.Sid)
		