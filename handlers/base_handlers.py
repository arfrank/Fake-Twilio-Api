from google.appengine.ext import webapp

from helpers import response, parameters, sid, authorization, xml
from decorators import authorization
import logging

class InstanceHandler(webapp.RequestHandler):
	@authorization.authorize_request
	def get(self,API_VERSION,ACCOUNT_SID, *args):
		format = response.response_format( args[0] )
		InstanceSid = args[0].split('.')[0]
		Instance = self.ModelInstance.filter('Sid =',InstanceSid).filter('AccountSid = ',ACCOUNT_SID).get()
		if Instance is not None and True:
			response_data = Instance.get_dict()
			response_data['ApiVersion'] = API_VERSION
			response_data['Uri'] = self.request.path
			if format == 'XML' or format == 'HTML':
				response_data = xml.add_nodes(response_data,'')
			self.response.out.write(response.format_response(response_data,format))
		else:
			self.error(400)

	@authorization.authorize_request
	def post(self, API_VERSION, ACCOUNT_SID, *args):
		if 'POST' in self.Allowed_Methods:
			pass
		else:
			self.error(405)
		
	@authorization.authorize_request
	def put(self, API_VERSION, ACCOUNT_SID, *args):
		if 'PUT' in self.Allowed_Methods:
			pass
		else:
			self.error(405)

	@authorization.authorize_request
	def delete(self, API_VERSION, ACCOUNT_SID, *args):
		if 'DELETE' in self.Allowed_Methods:
			format = response.response_format( args[0] )
			InstanceSid = args[0].split('.')[0]
			Instance = self.ModelInstance.filter('Sid = ',InstanceSid).get()
			if Instance is not None:
				db.delete(Instance)
				self.response.set_status(204)
			else:
				self.error(400)
		else:
			self.error(405)


class ListHandler(webapp.RequestHandler):
	@authorization.authorize_request
	def get(self,API_VERSION,ACCOUNT_SID, *args):
		self.error(400)

	@authorization.authorize_request
	def post(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)

	@authorization.authorize_request
	def put(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)

	@authorization.authorize_request
	def delete(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)