from google.appengine.ext import webapp

from helpers import response, parameters, sid, authorization, xml, uris, errors
from decorators import authorization
import math

class InstanceHandler(webapp.RequestHandler):
	@authorization.authorize_request
	def get(self,API_VERSION,ACCOUNT_SID, *args):
		format = response.response_format( args[0] )
		if 'GET' in self.AllowedMethods:
			InstanceSid = args[0].split('.')[0]
			Instance = self.ModelInstance.filter('Sid =',InstanceSid).filter('AccountSid = ',ACCOUNT_SID).get()
			if Instance is not None:
				response_data = Instance.get_dict()
				response_data['ApiVersion'] = API_VERSION
				response_data['Uri'] = self.request.path
				if format == 'XML' or format == 'HTML':
					response_data = xml.add_nodes(response_data,self.InstanceModelName)
				self.response.out.write(response.format_response(response_data,format))
			else:
				self.response.out.write(response.format_response(errors.rest_error_response(400,"The requested resource was not found",format),format))
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))

	@authorization.authorize_request
	def post(self, API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format( args[0] )
		if 'POST' in self.AllowedMethods:
			pass
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))
		
	@authorization.authorize_request
	def put(self, API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format( args[0] )
		if 'PUT' in self.AllowedMethods:
			pass
		else:
			self.response.out.write(response.format_response(errors.rest_error_response(405,"The requested method is not allowed",format,20004,'http://www.twilio.com/docs/errors/20004'),format))

	@authorization.authorize_request
	def delete(self, API_VERSION, ACCOUNT_SID, *args):
		format = response.response_format( args[0] )
		if 'DELETE' in self.AllowedMethods:
			format = response.response_format( args[0] )
			InstanceSid = args[0].split('.')[0]
			Instance = self.ModelInstance.filter('Sid = ',InstanceSid).get()
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
						self.ModelInstance.filter(query_filter[0]+query_filter[1],self.request.get(query_filter[0]))
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
			ListCount = self.ModelInstance.count()
			ListInstance = self.ModelInstance.fetch(PageSize,(Page*PageSize))
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

	#Unlikely this will be used ever
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
