import unittest
from helpers import twiml
import logging

class TwimlHelper_Check_Twiml_Response_Type(unittest.TestCase):
	def setUp(self):
		self.Twiml = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?><Response><Say>Hello</Say></Response>"
		self.Text = 'This is text to say'
		self.Audio = 'This is the information to play'
		self.TwimlHeaders = [{'Content-Type':'text/xml'},{'Content-Type':'application/xml'},{'Content-Type':'text/html'}]
		self.AudioHeaders = [ {'Content-Type':'audio/mpeg'}, {'Content-Type':'audio/wav'}, {'Content-Type':'audio/wave'}, {'Content-Type':'audio/x-wav'}, {'Content-Type':'audio/aiff'}, {'Content-Type':'audio/x-aifc'}, {'Content-Type':'audio/x-aiff'}, {'Content-Type':'audio/x-gsm'}, {'Content-Type':'audio/gsm'}, {'Content-Type':'audio/ulaw'} ]
		self.TextHeader = {'Content-Type':'text/plain'}
		self.TwimlRequests = []
		self.TextRequests = []
		self.AudioRequests = []
		self.FakePath = 'http://www.twilio.com/test.mp3'
		class FakeRequest(object):
			headers = {
				'Content-Type':''
			}
			path = ''
			content = 'THIS IS SOME BODY CONTENT'
			def __init__(self, content_type = None, path = None):
				if content_type != None:
					self.headers['Content-Type'] = content_type
				if path != None:
					self.path = path

		for head in self.TwimlHeaders:
			self.TwimlRequests.append(FakeRequest(content_type = head[ 'Content-Type' ] ) )
	
		for head in self.AudioHeaders:
			self.AudioRequests.append(FakeRequest(content_type = head[ 'Content-Type' ], path = self.FakePath ) )

		self.TextRequests.append(FakeRequest( content_type = self.TextHeader['Content-Type']))
	def test_Check_Twiml_Success_Twiml(self):
		for req in self.TwimlRequests:
			Valid, Twiml, TwilioCode, TwilioMsg = twiml.check_twiml( req )
			self.assertTrue(Valid)
	
	def test_Check_Twiml_Success_Text(self):
		Valid, Twiml, TwilioCode, TwilioMsg = twiml.check_twiml( self.TextRequests[0] )
		self.assertTrue(Valid)
		
	def test_Check_Twiml_Success_Audio(self):
		for req in self.AudioRequests:
			Valid, Twiml, TwilioCode, TwilioMsg = twiml.check_twiml( req )
			self.assertTrue(Valid)


class TwimlHelper_Processing_TwiML(unittest.TestCase):
	def setUp(self):
		#create account
		pass
	def test_Parse_Fail_Missing_Reponse_Twiml_Tag(self):
		Twiml = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?><Say>Hello</Say>"
		Valid, Twiml, ErrorMessage = twiml.parse_twiml(Twiml)
		self.assertFalse(Valid)
		
	def test_Parse_Fail_No_Content(self):
		Twiml = ""
		Valid, Twiml, ErrorMessage = twiml.parse_twiml(Twiml)
		self.assertFalse(Valid)
		
	def test_Parse_Fail_Nested_Elements(self):
		Twiml = """
<?xml version="1.0" encoding="UTF-8" ?>
<Response>
<Say>
<Play>http://twilio.com</Play>
</Say>
</Response>"""
		Valid, Twiml, ErrorMessage = twiml.parse_twiml(Twiml)
		logging.info( ErrorMessage )
		self.assertFalse(Valid)

	def test_Parse_Fail_Capitalize_Verb(self):
		Twiml = """<?xml version="1.0" encoding="UTF-8" ?>
		<Response>
		<say>This is the second one</say>
		</Response>"""
		Valid, Twiml, ErrorMessage = twiml.parse_twiml(Twiml)
		self.assertFalse(Valid)

	def test_Parse_Fail_Bad_Attributes(self):
		Twiml = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?><Response><Say length=10>Hello</Say></Response>"
		Valid, Twiml, ErrorMessage = twiml.parse_twiml(Twiml)
		self.assertFalse(Valid)
		
	def test_Parse_Fail_Dial_Children_None(self):
		pass
		
	def test_Parse_Fail_Dial_Children_Both_Number_Conference(self):
		pass
		
	def test_Parse_Fail_Dial_Children_MultiConference(self):
		pass

	def test_Parse_Fail_Dial_Children_Number_Twiml_Dial(self):
		pass