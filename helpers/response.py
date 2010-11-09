from django.utils import simplejson
from helpers import xml,html

def response_format(last_argument):
	split = last_argument.split('.')
	if len(split) > 1:
		return split[1].upper()
	else:
		return ''

def format_response(response_data,format):
	#Format response_data dictionary according to correct format guidelines
	"""docstring for format_response"""
	if format == 'JSON':
		return simplejson.dumps(response_data)
	elif format == 'CSV':
		pass
	elif format == 'HTML':
		return html.to_html(response_data)
	elif format == 'XML' or format == '':
		return xml.to_xml(response_data)


def add_nodes(self,response_data, format):
	if format == 'XML' or format == '' or format == 'HTML':
		response_data = {
			'TwilioResponse' : {
				self.InstanceModelName : response_data
				}
		}
	return response_data
	
def recording_format_response(self, response_data, format):
	if format == '':
		#WAV FORMAT
		#load a short wav file
	elif format == 'MP3':
		#MP3 Format
		#load a short mp3 file
	elif format == 'XML' or format == 'HTML' or format == 'JSON':
		return format_response(add_nodes(self,response_data,format),format)
