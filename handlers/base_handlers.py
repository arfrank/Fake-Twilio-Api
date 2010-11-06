from google.appengine.ext import webapp

class InstanceHandler(webapp.RequestHandler):
	@authorization.authorize_request
	def get(self,API_VERSION,ACCOUNT_SID, *args):
		InstanceSid = args[0]
		format = response.response_format(InstanceMessageSid)
		InstanceMessageSid = args[0].split('.')[0]
		Message = messages.Message.all().filter('Sid =',InstanceMessageSid).filter('AccountSid = ',ACCOUNT_SID).get()
		if Message is not None and True:
			response_data = Message.get_dict()
			response_data['ApiVersion'] = API_VERSION
			response_data['Uri'] = self.request.path
			if format == 'XML' or format == 'HTML':
				response_data = xml.add_nodes(response_data,'')
			self.response.out.write(response.format_response(response_data,format))
		else:
			self.error(400)

	def post(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)
		
	def put(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)

	def delete(self, API_VERSION, ACCOUNT_SID, *args):
		self.error(405)
