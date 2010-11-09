import urllib, urllib2, base64, hmac
from models import accounts
from google.appengine.ext import webapp
from google.appengine.api import memcache

from google.appengine.ext import db
from google.appengine.datastore import entity_pb

from helpers import errors,response
import urlparse
import logging

def authorize_request(method):
	def authorized_method(self, API_VERSION, ACCOUNT_SID, *args, **kwargs):
		if 'request' in kwargs:
			self.request = kwargs['request']

		if 'response' in kwargs:
			self.response = kwargs['response']

		format = response.response_format(self.request.path.split('/')[-1])
		logging.info(format)
		#Memcache the account to speed things up alittle
		#PREMATURE OPTIMIZATION!
		Account = memcache.get(ACCOUNT_SID)
		logging.info(ACCOUNT_SID)
		if Account is None:
			Account = accounts.Account.all().filter('Sid = ',ACCOUNT_SID).get()
			if Account is not None:
				memcache.set(ACCOUNT_SID,db.model_to_protobuf(Account).Encode())
		else:
			Account = db.model_from_protobuf(entity_pb.EntityProto(Account))
			#convert back from proto model
		logging.info(Account)
		if Account is not None:
			authstring = base64.encodestring(Account.Sid+':'+Account.AuthToken).replace('\n','')
			if 'Authorization' in self.request.headers: #hasattr(self.request.headers,'Authorization'):
				request_auth = self.request.headers['Authorization'].split(' ')
				if request_auth[0] == 'Basic' and request_auth[1]==authstring:
					self.data = {'Account' : Account}
					return method(self,API_VERSION,ACCOUNT_SID,*args,**kwargs)
				else:
					logging.info('Basic Authorization Failed')
					self.response.out.write(response.format_response(errors.rest_error_response(401,"Unauthorized",format),format))
			else:
				#should return a tuple of components, but documentation doesnt explain how to retrieve username & password
				parsed_url = urlparse.urlparse(self.request.url)
				netloc = parsed_url.netloc
				net_split = netloc.rsplit('@',1)
				if len(net_split) == 2:
					auth_info = net_split[0]
					auth_split = auth_info.split(':')
					if auth_split[0] == ACCOUNT_SID and auth_split[1] == Account.AuthToken:
						self.data = {'Account' : Account}
						return method(self,API_VERSION,ACCOUNT_SID,*args)
					else:
						self.response.out.write(response.format_response(errors.rest_error_response(401,"Authorization Required",format,20004),format))
				else:
					self.response.out.write(response.format_response(errors.rest_error_response(401,"Authorization Required",format,20004),format))
					
		else:
			logging.info('No account exists')
			self.response.out.write(response.format_response(errors.rest_error_response(400,"No Account Found",format),format))
			
	return authorized_method