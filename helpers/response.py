from django.utils import simplejson
from helpers import xml,html

def response_format(last_argument):
	split = last_argument.split('.')
	if len(split) > 1:
		return split[1].upper()
	else:
		return 'XML'

def format_response(response_data,format):
	"""docstring for format_response"""
	if format == 'JSON':
		return simplejson.dumps(response_data)
	elif format == 'XML':
		return xml.to_xml(response_data)
	elif format == 'CSV':
		pass
	elif format == 'HTML':
		return html.to_html(response_data)

def add_nodes(self,response_data, format):
	if format == 'XML' or format == 'HTML':
		response_data = {
			'TwilioResponse' : {
				self.InstanceModelName : response_data
				}
		}
	return response_data