from google.appengine.ext import webapp

from helpers import response, parameters, sid, authorization, xml, uris, errors
from decorators import authorization
import math

class InstanceHandler(webapp.RequestHandler):
	"""
	#EXAMPLE - for message
	def __init__(self):
		self.InstanceModel = messages.Message.all() 
		self.AllowedMethods = ['GET']
		self.AllowedFilters = {
			'GET':[['To','='],['From','='],['DateSent','=']]
		}
		self.ListName = 'SmsMessages'
		self.InstanceModelName = 'SmsMessage'
		#Only for Put and Post
		self.InstanceHelper = message_helper
		self.AllowedProperties = {
		'POST': [],
		'PUT': []
		}		
	"""
	@authorization.authorize_request
	def get(self,API_VERSION,ACCOUNT_SID, *args):
		if not len(args):
			args = [ACCOUNT_SID]
		format = response.response_format( args[0] )
		if 'GET' in self.AllowedMethods:
			InstanceSid = args[0].split('.')[0]
			if self.InstanceModelName == 'Account':
				#HACK
				Instance = self.InstanceModel.filter('Sid =',InstanceSid).get()
			else:
				logging.info('here')
				Instance = self.InstanceModel.filter('Sid =',InstanceSid).filter('AccountSid = ',ACCOUNT_SID).get()
			if Instance is not None:
				response_data = Instance.get_dict()
				response_data['ApiVersion'] = API_VERSION
				response_data['Uri'] = self.request.path
				self.response.out.write(response.format_response(response.add_nodes(self,response_data,format),format))
			else:
				self.response.out.write(response.format_response(errors.rest_error_response(404,"The requested resource was not found",format),format))
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))

	@authorization.authorize_request
	def post(self, API_VERSION, ACCOUNT_SID, *args, **kwargs):
		if 'request' in kwargs:
			request = kwargs['request']
		else:
			request = self.request
		format = response.response_format( args[0] )
		if 'POST' in self.AllowedMethods:
			InstanceSid = args[0].split('.')[0]
			Instance = self.InstanceModel.filter('Sid =',InstanceSid).filter('AccountSid = ',ACCOUNT_SID).get()
			if Instance is not None:
				#update stuff according to allowed rules
				#get all arguments passed in
				Valid = True
				TwilioCode = 0
				TwilioMsg = ''
				index = 0
				arg_length = len(request.arguments())
				arg_list = request.arguments()
				while Valid and index < arg_length:
					#if we are allowed to alter that argument
					if arg_list[index] in self.AllowedProperties['POST']:
						#validate that a valid value was passed in
						Valid,TwilioCode,TwilioMsg =  Instance.validate(request, arg_list[index], request.get( arg_list[index] ))
							#set it to a valid argument value
						if Valid:
							setattr(Instance, arg_list[index], Instance.sanitize( request, arg_list[index], request.get( arg_list[index] )))
				if Valid:
					Instance.put()
					InstanceHandler.get(self,API_VERSION,ACCOUNT_SID,*args)
				else:
					self.response.out.write(response.format_response(errors.rest_error_response(400,"You have made a bad request",format,TwilioCode,TwilioMsg),format))					
			else:
				self.response.out.write(response.format_response(errors.rest_error_response(404,"The requested resource was not found",format),format))
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))
		
	@authorization.authorize_request
	def put(self, API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format( args[0] )
		if 'PUT' in self.AllowedMethods:
			InstanceHandler.post(self,API_VERSION,ACCOUNT_SID,*args)
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))

	@authorization.authorize_request
	def delete(self, API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format( args[0] )
		if 'DELETE' in self.AllowedMethods:
			format = response.response_format( args[0] )
			InstanceSid = args[0].split('.')[0]
			Instance = self.InstanceModel.filter('Sid = ',InstanceSid).get()
			if Instance is not None:
				db.delete(Instance)
				self.response.set_status(204)
			else:
				self.error(400)
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))


class ListHandler(webapp.RequestHandler):
	@authorization.authorize_request
	def get(self,API_VERSION,ACCOUNT_SID, *args):
		format = response.response_format(self.request.path.split('/')[-1])
		if 'GET' in self.AllowedMethods:
			if hasattr(self.AllowedFilters,'GET'):
				for query_filter in self.AllowedFilters['GET']:
					if query_filter[0] in self.request.arguments():
						self.InstanceModel.filter(query_filter[0]+query_filter[1],self.request.get(query_filter[0]))
						#NEEDS TO TAKE INTO ACCOUNT DATES
			try:
				Page = int(self.request.get('Page',0))
			except Exception, e:
				Page = 0
			if Page < 0:
				Page = 0
			try:
				PageSize = int(self.request.get('PageSize',50))
			except Exception, e:
				PageSize = 50
			if PageSize > 1000:
				PageSize = 1000
			if PageSize < 0:
				PageSize = 50
			ListCount = self.InstanceModel.count()
			ListInstance = self.InstanceModel.fetch(PageSize,(Page*PageSize))
			End = PageSize+(Page*PageSize) if ( ListCount < (PageSize+(Page*PageSize)) )  else ListCount
			response_data = {
							"start": (Page*PageSize),
							"end": End,
							"total": ListCount,
							"pagesize": PageSize,
							"numpages": int(math.ceil(float(ListCount)/PageSize)),
							"page":Page,
							"uri": uris.CurUri(self.request.path,self.request.query_string),
							"firstpageuri": uris.FirstUri(Page,PageSize,ListCount,self.request.path),
							"nextpageuri": uris.NextUri(Page,PageSize,ListCount,self.request.path),
							"previouspageuri": uris.PrevUri(Page,PageSize,ListCount,self.request.path),
							"lastpageuri": uris.LastUri(Page,PageSize,ListCount,self.request.path),
							self.ListName:[]
							}
			for instance in ListInstance:
				response_data[self.ListName].append({self.InstanceModelName : instance.get_dict()})
			self.response.out.write(response.format_response(response_data,format))
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))

	#Unlikely this will be used ever, or can I generalize this to allow for reuse.
	@authorization.authorize_request
	def post(self, API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format(self.request.path.split('/')[-1])
		if 'POST' in self.AllowedMethods:
			pass
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))

	#Unlikely this will be used ever
	@authorization.authorize_request
	def put(self, API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format(self.request.path.split('/')[-1])
		if 'PUT' in self.AllowedMethods:
			pass
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))

	#Unlikely this will be used ever
	@authorization.authorize_request
	def delete(self, API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format(self.request.path.split('/')[-1])
		if 'DELETE' in self.AllowedMethods:
			pass
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))
