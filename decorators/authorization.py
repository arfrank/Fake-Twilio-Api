import urllib, urllib2, base64, hmac
from models import accounts
from google.appengine.ext import webapp
from google.appengine.api import memcache

from google.appengine.ext import db
from google.appengine.datastore import entity_pb

from helpers import errors,response

import logging

def authorize_request(method):
	def authorized_method(self,API_VERSION,ACCOUNT_SID,*args):
		format = response.response_format(self.request.path.split('/')[-1])
		#Memcache the account to speed things up alittle
		#PREMATURE OPTIMIZATION!
		Account = memcache.get('ACCOUNT_SID')
		if Account is None:
			Account = accounts.Account.all().filter('Sid = ',ACCOUNT_SID).get()
			if Account is not None:
				memcache.set(ACCOUNT_SID,db.model_to_protobuf(Account).Encode())
		else:
			Account = db.model_from_protobuf(entity_pb.EntityProto(Account))
			#convert back from proto model

		if Account is not None:
			authstring = base64.encodestring(Account.Sid+':'+Account.AuthToken).replace('\n','')
			if 'Authorization' in self.request.headers:#hasattr(self.request.headers,'Authorization'):
				request_auth = self.request.headers['Authorization'].split(' ')
				if request_auth[0] == 'Basic' and request_auth[1]==authstring:
					self.data = {'Account' : Account}
					return method(self,API_VERSION,ACCOUNT_SID,*args)
				else:
					logging.info('Basic Authorization Failed')
					self.response.out.write(response.format_response(errors.rest_error_response(401,"Unauthorized",format),format))
					
			else:
				logging.info('No authorization header')
				self.response.out.write(response.format_response(errors.rest_error_response(401,"Authorization Required",format,20004),format))
		else:
			logging.info('No account exists')
			self.response.out.write(response.format_response(errors.rest_error_response(400,"No Account Found",format),format))
			
	return authorized_method