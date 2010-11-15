import unittest
import logging
from google.appengine.ext import db
import models

class CallModel(unittest.TestCase):
	def setUp(self):
		#create account
		self.Account  = models.accounts.Account.new(key_name='email@email.com',email='email@email.com',password='password')
		self.Account.put()
		self.PhoneNumber,Valid,TwilioCode, TwilioMsg = models.incoming_phone_numbers.Incoming_Phone_Number.new(PhoneNumber = '+13015559999', request = None, AccountSid = self.Account.Sid)
		self.OutgoingCallerId, Valid, TwilioCode, TwilioMsg = models.outgoing_caller_ids.Outgoing_Caller_Id.new(PhoneNumber = '+13015556666', request = None, AccountSid = self.Account.Sid)
		db.put([self.PhoneNumber, self.OutgoingCallerId])
		self.FakeToNumber = '+12405551234'
		
	def test_Call_Creation_Success_Full_Lifecycle(self):
		Call, Valid, TwilioCode, TwilioMsg = models.calls.Call.new(To = self.FakeToNumber, From = self.PhoneNumber.PhoneNumber, request = None, Direction = 'outbound-api', AccountSid = self.Account.Sid, Status = 'queued')
		self.assertTrue(Valid)
		self.assertEqual(Call.Status,'queued')
		Call.ring()
		self.assertEqual(Call.Status,'ringing')
		Call.connect()
		self.assertEqual(Call.Status,'in-progress')
		Call.disconnect()
		self.assertEqual(Call.Status,'complete')
		
	def test_Call_Creation_Success_Outgoing_Caller_Id_Full_Lifecycle(self):
		Call, Valid, TwilioCode, TwilioMsg = models.calls.Call.new(To = self.FakeToNumber, From = self.OutgoingCallerId.PhoneNumber, request = None, Direction = 'outbound-api', AccountSid = self.Account.Sid, Status = 'queued')
		self.assertTrue(Valid)
		self.assertEqual(TwilioCode, 0)
		self.assertEqual(Call.Status,'queued')
		Call.ring()
		self.assertEqual(Call.Status,'ringing')
		Call.connect()
		self.assertEqual(Call.Status,'in-progress')
		Call.disconnect()
		self.assertEqual(Call.Status,'complete')
			
	def test_Call_Creation_Success_Busy(self):
		Call, Valid, TwilioCode, TwilioMsg = models.calls.Call.new(To = self.FakeToNumber, From = self.PhoneNumber.PhoneNumber, request = None, Direction = 'outbound-api', AccountSid = self.Account.Sid, Status = 'queued')
		self.assertTrue(Valid)
		self.assertEqual(Call.Status,'queued')
		Call.ring()
		self.assertEqual(Call.Status,'ringing')
		Call.busy()
		self.assertEqual(Call.Status,'busy')


	def test_Call_Failure_Invalid_To_Number(self):
		Call, Valid, TwilioCode, TwilioMsg = models.calls.Call.new(To = '+12123123', From = self.PhoneNumber.PhoneNumber, request = None, Direction = 'outbound-api', AccountSid = self.Account.Sid)
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 21401)
		
	def test_Call_Failure_Invalid_From_Number(self):
		Call, Valid, TwilioCode, TwilioMsg = models.calls.Call.new(To = self.FakeToNumber, From = '+14105553232', request = None, Direction = 'outbound-api', AccountSid = self.Account.Sid)
		self.assertFalse(Valid)
		self.assertEqual(TwilioCode, 14108)
