from google.appengine.api import urlfetch
import urllib
from helpers import authorization
import logging
#returns the response object
def request_twiml(Account, Url, Method, Payload):
	if Method == 'GET':
		url = Url + '?' +'&'.join(k+'='+v for k,v in Payload.iteritems())
		Twilio_Signature = authorization.create_twilio_authorization_hash(Account, Url, Payload, Method = 'GET')
		response = urlfetch.fetch(url = url,method = urlfetch.GET, headers = {'X-Twilio-Signature':Twilio_Signature} )							
	else:
		Twilio_Signature = authorization.create_twilio_authorization_hash(Account, Url, Payload, Method='POST')
		response = urlfetch.fetch(url = Url,method = urlfetch.POST, payload = urllib.urlencode(Payload) , headers = {'X-Twilio-Signature':Twilio_Signature} )
	return response