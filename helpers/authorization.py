import urllib, urllib2, base64, hmac
from hashlib import sha1

def authorize_request(Account,request):
	if Account is not None:
		authstring = base64.encodestring(Account.Sid+':'+Account.AuthToken).replace('\n','')
		if hasattr(request.headers,'Authorization'):
			request_auth = request.headers['Autorization'].split(' ')
			if request_auth[0] == 'Basic':
				return request_auth[1]==authstring
			else:
				return False
		else:
			return False
	else:
		return False
		
##STOLEN FROM TWILIO UTILITY CLASS
def create_twilio_authorization_hash(Account,URL,Payload):
	Hash_String = URL
	if len(Payload) > 0:
		for k, v in sorted(Payload.items()):
			Hash_String += k + v
	return base64.encodestring(hmac.new(Account.AuthToken, Hash_String, sha1).digest())
