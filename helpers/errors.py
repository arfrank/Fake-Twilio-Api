def rest_error_response(Status,Message,Format = 'XML',TwilioCode = None,TwilioMessage = None):
	response = {
	"Status" : Status,
	"Message" : Message
	}
	if TwilioCode is not None:
		response['Code'] = TwilioCode
	if TwilioMessage is not None:
		response['MoreInfo'] = TwilioMessage
	if Format == 'XML' or Format == 'HTML':
		response = {
					'TwilioResponse' : {
						'RestException' : response
						}
					}
	return response
	