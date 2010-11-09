from google.appengine.ext import db
import datetime
import logging

class CommonModel(db.Model):
	DateCreated = db.DateTimeProperty(auto_now_add = True)
	DateUpdated = db.DateTimeProperty(auto_now = True)
	
	def get_dict(self):
		object_dict = {}
		for key in self.properties():
			if type(getattr(self,key)) == datetime.datetime:
				#not given twilio format, but shouldnt really break it for anyone really, will fix later
				object_dict[key] = getattr(self,key).isoformat()
				#.strpformat('%M-%D-%Y %H:%I:%S %z) #not right
			else:
				object_dict[key] = getattr(self,key)	
		return object_dict

# Base functions to be overloaded to ensure that they exist
	def sanitize(self, request, arg_name, arg_value):
		return arg_value

	def validate(self, request, arg_name, arg_value):
		return True