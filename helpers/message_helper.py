from helpers import parameters

def validate(self,arg_name,arg_value):
	validators = {
		'FriendlyName' : self.request.get('FriendlyName',None),
		'VoiceCallerIdLookup' : parameters.allowed_boolean(self.request.get('VoiceCallerIdLookup',None)),
		'VoiceUrl' : parameters.standard_urls(self.request.get('VoiceUrl',None))
		'VoiceMethod' : parameters.allowed_methods(arg_value,['GET','POST']),
		'VoiceFallbackUrl' : self.request.get('VoiceFallbackUrl',None),
		'VoiceFallbackMethod' : parameters.allowed_methods(arg_value,['GET','POST']),
		'StatusCallback' : self.request.get('StatusCallback',None),
		'StatusCallbackMethod' : parameters.allowed_methods(arg_value,['GET','POST']),
		'SmsUrl' : self.request.get('SmsUrl',None),
		'SmsMethod' : parameters.allowed_methods(arg_value,['GET','POST']),
		'SmsFallbackUrl' : self.request.get('SmsFallbackUrl',None),
		'SmsFallbackMethod' : parameters.allowed_methods(arg_value,['GET','POST'])
	}
	
	return True
	
def sanitize(self,arg_name,arg_value):
	santizers = {
		'FriendlyName' : self.request.get('FriendlyName',None),
		'VoiceCallerIdLookup' : self.request.get('VoiceCallerIdLookup',None),
		'VoiceUrl' : self.request.get('VoiceUrl',None),
		'VoiceMethod' : parameters.methods(arg_name,self.request,'POST'),
		'VoiceFallbackUrl' : self.request.get('VoiceFallbackUrl',None),
		'VoiceFallbackMethod' : parameters.methods(arg_name,self.request,'POST'),
		'StatusCallback' : self.request.get('StatusCallback',None),
		'StatusCallbackMethod' : parameters.methods(arg_name,self.request,'POST'),
		'SmsUrl' : self.request.get('SmsUrl',None),
		'SmsMethod' : parameters.methods(arg_name,self.request,'POST'),
		'SmsFallbackUrl' : self.request.get('SmsFallbackUrl',None),
		'SmsFallbackMethod' : parameters.methods(arg_name,self.request,'POST')
	}
	return arg_value
