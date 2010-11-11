from google.appengine.ext import webapp

from helpers import response, parameters, sid, authorization, xml, uris, errors
from decorators import authorization
import math
import logging
from google.appengine.ext import db

class InstanceHandler(webapp.RequestHandler):
	def __init__(self):
		self.LastSidName = 'Sid'
		self.AdditionalFilters = []
	"""
	self.InstanceModel = phone_numbers.Phone_Number.all()
	self.AllowedMethods = ['GET','POST','PUT','DELETE']
	self.InstanceModelName = 'IncomingPhoneNumber'
	self.AllowedProperties = {
		'POST' : ['FriendlyName','ApiVersion','VoiceUrl','VoiceMethod','VoiceFallbackUrl','VoiceFallbackMethod','StatusCallback','StatusCallbackMethod','SmsUrl','SmsMethod','SmsFallbackUrl','SmsFallbackMethod','VoiceCallerIdLookup'],
		'PUT' : ['FriendlyName','ApiVersion','VoiceUrl','VoiceMethod','VoiceFallbackUrl','VoiceFallbackMethod','StatusCallback','StatusCallbackMethod','SmsUrl','SmsMethod','SmsFallbackUrl','SmsFallbackMethod','VoiceCallerIdLookup']
	}
	"""	
	@authorization.authorize_request
	def get(self,API_VERSION,ACCOUNT_SID, *args):
		#hack for accounts having short urls
		if not len(args):
			args = [ACCOUNT_SID]
		format = response.response_format( args[-1] )
		if 'GET' in self.AllowedMethods:
			#Get the instanceSid from the url
			InstanceSid = args[-1].split('.')[-1]
			#Use the lastsidname to filter, usually will just be sid, but can be something different
			self.InstanceModel.filter(self.LastSidName+' =',InstanceSid).get()
			#Only needed for compatabilty with Accounts because Accounts dont have Sids
			if self.InstanceModelName != 'Account':
				Instance = self.InstanceModel.filter('AccountSid = ',ACCOUNT_SID)
			#Might not exist, since its only used for special cases with long urls
			if hasattr(self,'AdditionalFilter'):
				for addfilter in self.AdditionalFilters:
					Instance.filter(addfilter[0],args[addfilter[1]])
			Instance = self.InstanceModel.get()
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
		#HACK TO LET ACCOUNTS WORK
		if not len(args):
			args = [ACCOUNT_SID]
		if 'request' in kwargs:
			request = kwargs['request']
		else:
			request = self.request
		format = response.response_format( args[-1] )
		if 'POST' in self.AllowedMethods:
			InstanceSid = args[-1].split('.')[-1]
			self.InstanceModel.filter(self.LastSidName+' =',InstanceSid)
			if self.InstanceModelName != 'Account':
				self.InstanceModel.filter('AccountSid = ',ACCOUNT_SID)
			Instance = self.InstanceModel.get()
			if Instance is not None:
				#update stuff according to allowed rules
				#get all arguments passed in
				Valid = True
				for arg in request.arguments():
					#if we are allowed to alter that argument
					if arg in self.AllowedProperties['POST']:
						#validate that a valid value was passed in
						if Valid:
							Valid, TwilioCode, TwilioMsg =  Instance.validate(request, arg, request.get( arg ))
							#set it to a valid argument value
							if Valid:
								setattr(Instance, arg, Instance.sanitize( request, arg, request.get( arg )))
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
		format = response.response_format( args[-1] )
		if 'PUT' in self.AllowedMethods:
			#Cheating and just using post for now
			InstanceHandler.post(self,API_VERSION,ACCOUNT_SID,*args)
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))

	@authorization.authorize_request
	def delete(self, API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format( args[-1] )
		if 'DELETE' in self.AllowedMethods:
			format = response.response_format( args[-1] )
			InstanceSid = args[-1].split('.')[-1]
			Instance = self.InstanceModel.filter('Sid = ',InstanceSid).get()
			if Instance is not None:
				db.delete(Instance)
				self.response.set_status(204)
			else:
				self.response.out.write(response.format_response(errors.rest_error_response(404,"The requested resource was not found",format),format))
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))


class ListHandler(webapp.RequestHandler):
	def __init__(self):
		self.AdditionalFilter = []
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
		self.AllowedProperties = {
		'POST': [],
		'PUT': []
		}		
	"""
	
	@authorization.authorize_request
	def get(self,API_VERSION,ACCOUNT_SID, *args):
		format = response.response_format(self.request.path.split('/')[-1])
		if 'GET' in self.AllowedMethods:
			if hasattr(self.AllowedFilters,'GET'):
				for query_filter in self.AllowedFilters['GET']:
					if query_filter[0] in self.request.arguments():
						self.InstanceModel.filter(query_filter[0]+query_filter[1],self.request.get(query_filter[0]))
						#NEEDS TO TAKE INTO ACCOUNT DATES
			if hasattr(self,'AdditionalFilter'):
				for addfilter in self.AdditionalFilter:
					self.InstanceModel.filter(addfilter[0],addfilter[1])
			try:
				Page = int(self.request.get('Page',0))
			except Exception, e:
				Page = 0
			else:
				if Page < 0:
					Page = 0
			try:
				PageSize = int(self.request.get('PageSize',50))
			except Exception, e:
				PageSize = 50
			else:
				if PageSize > 1000:
					PageSize = 1000
				elif PageSize < 0:
					PageSize = 50
			ListCount = self.InstanceModel.count()
			ListInstance = self.InstanceModel.fetch(PageSize,(Page*PageSize))
			End = PageSize+(Page*PageSize) if ( ListCount < ( PageSize+( Page*PageSize ) ) )  else ListCount
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
