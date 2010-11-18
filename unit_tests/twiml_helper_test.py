import unittest
from helpers import twiml
import logging

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