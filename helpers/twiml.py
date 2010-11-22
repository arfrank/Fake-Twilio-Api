from xml.parsers.expat import ExpatError

from xml.dom import minidom
from google.appengine.api import urlfetch

from models import calls, messages, transcriptions, conferences, participants, notifications, recordings, twimls, accounts

from helpers import request, errors

import logging
import pickle
import urlparse

ALLOWED_VOICE_ELEMENTS = {
'Say' : ['voice','language','loop'],
'Play':['loop'],
'Gather':['action','method','timeout','finishOnKey','numDigits'],
'Record':['action','method','timeout','finishOnKey','maxLength','transcribe','transcribeCallback','playBeep'],
'Sms':['to','from','action','method','statusCallback'],
'Dial':['action','method','timeout','hangupOnStar','timeLimit','callerId'],
'Number':['sendDigits','url'],
'Conference':['muted','beep','startConferenceOnEnter','endConferenceOnExit','waitUrl','waitMethod'],
'Hangup':[],
'Redirect':['method'],
'Reject':['reason'],
'Pause':['length']
}

ALLOWED_SMS_ELEMENTS = {
		'Sms' : ['to','from','action','method','statusCallback'],
		'Redirect' : ['method']
	}

ALLOWED_SUBELEMENTS = {
	'Gather': ['Say', 'Play', 'Pause'],
	'Dial':['Number', 'Conference']
}
"""
#ADAPTED FROM https://github.com/minddog/twilio-emulator

Twilio Emulator

----------------------------------------------------
A python based twilio call flow emulator that allows 
user interaction for dialogs and timeouts.  It is 
designed to speed up development of your application 
without dialing a phone and saving telephony costs.

Copyright(c) 2009 Adam Ballai <aballai@gmail.com>
----------------------------------------------------
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. The name of the author may not be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

def emulate(url, method = 'GET', digits = None):
	logger.notice('[Emulation Start] %s' % url)
	response = getResponse(
		url,
		method,
		digits)
	if not response:
		logger.error('[Emulation Failed to start]')
		exit_handler()
	
	try:
		rdoc = parseString(response)
	except ExpatError, e:
		raise TwiMLSyntaxError(e.lineno, e.offset, response)

	try:
		respNode = rdoc.getElementsByTagName('Response')[0]
	except IndexError, e:
		logger.error('[No response node] exiting')
		exit_handler()
	
	if not respNode.hasChildNodes():
		#hangup
		logger.notice('Hanging up')
		exit_handler()
		
	nodes = respNode.childNodes
	for node in nodes:
		if node.nodeType == node.TEXT_NODE:
			# ignore
			pass
		if node.nodeType == node.ELEMENT_NODE:
			request = processNode(node)
			if not request:
				continue
			try:
				if(request['action'] == ''):
					request['action'] = url
				emulate(request['action'], 
						request['method'], 
						request['digits'])
			except TwiMLSyntaxError, e:
				logger.error(e)
				exit_handler()
"""

class TwiMLSyntaxError(Exception):
	def __init__(self, error, code, msg):
		self.error = error
		self.code = code
		self.msg = msg		

	def __str__(self):
		return "%s\nTwilioCode: %s TwilioMsg: %s" \
			% (self.error, str(self.code), self.msg)

#Returns valid, twiml_object, twilio code, twilio message
def parse_twiml(response, sms = False, allow_dial = True):
	try:
		rdoc = minidom.parseString(response)
	except ExpatError, e:
		return False, False, 12100, 'http://www.twilio.com/docs/errors/12100'

	try:
		respNode = rdoc.getElementsByTagName('Response')[0]
	except IndexError, e:
		return False, False, 12100, 'http://www.twilio.com/docs/errors/12100'

	if not respNode.hasChildNodes():
		return False, False, 12100, 'http://www.twilio.com/docs/errors/12100'
	nodes = respNode.childNodes
	try:
		twiml_object = walk_tree(nodes,'Response', sms = sms, allow_dial = allow_dial)
	except TwiMLSyntaxError, e:
		return False, False, e.code, e.msg
	#lets walk the tree and create a list [ { 'Verb' : '', 'Attr': { 'action' : '', 'Method' : 'POST' } } ]
	else:
		return True, twiml_object, 0, ''

def retrieve_attr(node, Type, sms = False):
	d = {}
	for attr in node.attributes.items():
		if (sms == False and attr[0] in ALLOWED_VOICE_ELEMENTS[Type]) or (sms == True and attr[0] in ALLOWED_SMS_ELEMENTS[Type]):
			d[attr[0]] = attr[1]
		else:
			raise TwiMLSyntaxError('Invalid attribute in '+Type+':('+attr[0]+'='+attr[1]+')', 12200,'http://www.twilio.com/docs/errors/12200')
	return d

def walk_tree(nodes, parentType, sms = False, allow_dial = True):
	twiml = []
	count = 0
	for node in nodes:
		if node.nodeType == node.ELEMENT_NODE:
			#If its an element, makes 
			#logging.info(parentType)
			#logging.info(node.nodeName.encode('ascii'))
			#logging.info(sms)
			#if we are at the top level of the response, and we are in the allowed verbs for the request type, or we are a valid subelement
			nodeName = node.nodeName.encode( 'ascii' )

			if ( ( parentType == 'Response' and ( ( nodeName in ALLOWED_SMS_ELEMENTS and sms == True) or ( nodeName in ALLOWED_VOICE_ELEMENTS and sms == False ) ) ) or ( parentType in ALLOWED_SUBELEMENTS ) ):

				if allow_dial == False and nodeName == 'Dial':

					raise TwiMLSyntaxError( 'Cannot Dial out from a dial call segment', 13201, 'http://www.twilio.com/docs/errors/13201' )

				if parentType == 'Response' or  node.nodeName.encode('ascii') in ALLOWED_SUBELEMENTS[parentType]:

					check_twiml_verb_attr(node)

					check_twiml_verb_children(node)

					twiml.append( { 'Type' : node.nodeName.encode( 'ascii' ), 'Attr' : retrieve_attr(node, node.nodeName.encode('ascii'), sms),'Children': walk_tree(node.childNodes, node.nodeName.encode('ascii'), sms = sms) } )

				else:

					raise TwiMLSyntaxError('Invalid TwiML nested element in '+parentType+'. Not allowed to nest '+node.nodeName.encode('ascii'), 12200, 'http://www.twilio.com/docs/errors/12200')					

			else:

				raise TwiMLSyntaxError( 'Invalid TwiML in ' + parentType + '. Problem with '+node.nodeName.encode('ascii')+' element ('+str(count)+')', 12200, 'http://www.twilio.com/docs/errors/12200' )

		elif node.nodeType == node.TEXT_NODE and parentType != 'Response':

			if node.nodeValue.encode('ascii') != '\n':

				twiml.append( { 'Type' : 'Text', 'Data': node.nodeValue.encode('ascii') })

		count +=1
		
	return twiml

def check_twiml_verb_attr(node):
	name = node.nodeName.encode( 'ascii' )
	if name == 'Dial':
		pass
	elif name == 'Conference':
		pass
	elif name == 'Number':
		pass
	
def check_twiml_dial_attr():
	"""docstring for check_twiml_dial_attr"""
	pass

def check_twiml_conference_attr():
	"""docstring for check_twiml_conference_attr"""
	pass
	
def check_twiml_number_attr():
	"""docstring for check_twiml_number_attr"""
	pass
	
def check_twiml_verb_children(node):
	verb = node.nodeName.encode( 'ascii' )
	if verb == 'Dial':
		#should be a seperate function, but right now this is the only place where it matters"
		if not len(node.childNodes):
			raise TwiMLSyntaxError( 'The dial verb needs to have nested nouns', 12100, 'http://www.twilio.com/docs/errors/12100' )
		else:
			conf = False
			num = False
			for child in node.childNodes:
				if child.nodeName.encode( 'ascii' ) == 'Conference':
					conf = True
				elif child.nodeName.encode( 'ascii' ) == 'Number':
					num = True
			if num and conf:
				raise TwiMLSyntaxError( 'Cannot have nested Number and Conference in the same Dial Verb', 12100, 'http://www.twilio.com/docs/errors/12100' )
				

def check_twiml_content_type(response):
	TWIML_CONTENT_TYPES = ['text/xml','application/xml','text/html']
	TEXT_CONTENT_TYPES = ['text/plain']
	AUDIO_CONTENT_TYPES = ['audio/mpeg', 'audio/wav', 'audio/wave', 'audio/x-wav', 'audio/aiff', 'audio/x-aifc', 'audio/x-aiff', 'audio/x-gsm', 'audio/gsm', 'audio/ulaw']
	if response.headers['Content-Type'] in TWIML_CONTENT_TYPES:
		content = str(response.content).replace('\n','')
		return True, content, 0, ''
	elif response.headers['Content-Type'] in TEXT_CONTENT_TYPES:
		content = """<?xml version="1.0" encoding="UTF-8" ?><Response><Say>""" + response.content + """</Say></Response>"""
		return True, content, 0, ''
	elif response.headers['Content-Type'] in AUDIO_CONTENT_TYPES:
		content = """<?xml version="1.0" encoding="UTF-8" ?><Response><Play>""" + response.path + """</Play></Response>"""
		return True, content, 0, ''
	else:
		return False, '', 12300, 'http://www.twilio.com/docs/errors/12300'

# ABOVE PROCESSING TwiML
#############################################################################################
# BELOW PROCESSING CONSOLE FUNCTIONS

def process_say(verb):
	#logging.info('process say')
	return (process_text(verb),False,False)

def process_play(verb):
	logging.info('process play')
	return ('Playing audio from '+process_text(verb),False,False)

def process_record(verb, Twiml, ModelInstance, Input = ''):
	msg = ''
	error = False
	#BAD SYSTEM but it should work
	try:
		dur = int(Input)
	except Exception, e:
		dur = ''
	if dur != '':
		if dur == 0:
			return 'No recording made',False,False
		else:
			maxLength = verb['Attr']['maxLength'] if 'maxLength' in verb['Attr'] else 3600
			try:
				maxLength = int(maxLength)
			except Exception, e:
				maxLength = 3600
			if dur > maxLength:
				dur = maxLength

			#'Record':['action','method','timeout','finishOnKey','maxLength','transcribe','transcribeCallback','playBeep'],
			Recording, Valid, TwilioCode, TwilioMsg = recordings.Recording.new(
											AccountSid = ModelInstance.AccountSid,
											CallSid = ModelInstance.Sid,
											Duration = dur
										)
			#logging.info('process record')
			msg += 'A recording has been made\n'
			if Valid:
				Action = verb['Attr']['action']	if 'Attr' in verb and 'action' in verb['Attr'] else None
				Method = verb['Attr']['method'] if 'Attr' in verb and 'method' in verb['Attr'] else 'POST'
				if Action is None:
					Action = Twiml.Url
				NewDoc = False
				if Action is not None:
					Account = accounts.Account.all().filter('Sid =',ModelInstance.AccountSid).get()
					
					#Whether or not twiml parsed, the twiml dictionary, and any error messages
					Valid, Twiml, AddMessage = get_external_twiml(Account, Action, Method, ModelInstance, {'SmsSid' : Instance.Sid, 'SmsStatus' : Message.Status}, OTwiml)
				msg+=AddMessage
				if 'transcribe' in verb['Attr'] and verb['Attr']['transcribe'] == 'true':
					transcribeCallback = verb['Attr']['transcribeCallback'] if 'Attr' in verb and 'transcribeCallback' in verb['Attr'] else None
					Recording.transcribe(transcribeCallback)
					msg+='A transcription has been made\n'
				if NewDoc:
					msg+='A new Twiml document was created, processing will continue on that document\n'
					return msg, True, Twiml
				else:
					return msg, False, False
			else:
				return 'Recording failed', False, False
	else:
		#need to inform the person of a recording happening
		msg += 'Recording in progress.\n'
		msg += 'BEEP\n' if 'playBeep' in verb['Attr'] and verb['Attr']['playBeep'] == 'true' else ''
		msg += 'Max Length: '+verb['Attr']['maxLength']+'\n' if 'maxLength' in verb['Attr'] else ''
		msg += 'Timeout: '+verb['Attr']['timeout']+'\n' if 'timeout' in verb['Attr'] else ''
		msg += 'Will Transcribe\n' if 'transcribe' in verb['Attr'] and verb['Attr']['transcribe'] == 'true' else ''
		msg += 'Please enter how long you would like the recording to be (0 means no recording will be made - equivalent to timing out)'
		return msg, True, False

def process_pause(verb):
	#logging.info('process pause')
	if 'Attr' in verb and 'length' in verb['Attr']:
		return ('Pausing for '+verb['Attr']['length']+' seconds',False,False)
	else:
		return ('Pausing for 1 second',False,False)

# What does a gather do?
# It waits for a response
# HOW DO WE TIMEOUT?????????? right now if you respond with T it's a timeout
# Currently a blank response will cause it to reparse the document
# 'Gather':['action','method','timeout','finishOnKey','numDigits'],

def process_gather(verb, Twiml, ModelInstance, Input):
	msg = ''
	#logging.info(Input)
	ALLOWED_RESPONSE = ['0','1','2','3','4','5','6','7','8','9','#','*']
	#BAD SYSTEM but it should work
	#Parse the input! - should just check that characters in 0-9 # *, dont know what my mind was thinking originally
	dur = Input
	for el in Input:
		if el not in ALLOWED_RESPONSE:
			dur = ''
			break
	#override for timeout
	if Input == 'T':
		dur = 'T'
	#If no input, just replay that we are waiting for input
	if dur == '':
		numDigits = '\nmaximum Number of digits: '+verb['Attr']['numDigits']+'\n' if 'numDigits' in verb['Attr'] else '\n'
		if len(verb['Children']):
			msg = 'Gathering your response, nested elements to follow'+numDigits
			for node in verb['Children']:
				response, Break, newTwiml = process_verb(node, Twiml, ModelInstance, '')
				msg += response + '\n'
				if Break:
					break
			return msg, True, False
		else:
			msg = 'Gathering your response'+numDigits
			return msg, True, False
	else:
		#check the length of the response, also strip extra
		badLength = False
		try:
			#try and get max num of digits
			length = int(verb['Attr']['numDigits'])
		except ValueError, e:
			#no a number in the twiml, 
			#logging.info('unable to process length, not a number')
			msg = 'Unable to parse numDigits in Twiml, not a number\nMoving onto the next verb\n'
			badLength = True
			Break = False
		except KeyError, e:
			#logging.info('unable to process length, not in Attr')
			pass
		else:
			if len(str(dur)) > length:
				badLength = True
				Break = True
				msg = 'You have entered too many digits. Please try again\n'

		#we have a response that we like
		if badLength:
			return msg, Break, False
		else:
			if dur == 'T':
				return 'No gather was recorded (timeout), will continue on parsing', False, False
			else:
				Account = accounts.Account.all().filter('Sid =', ModelInstance.AccountSid).get()
				#'Gather':['action','method','timeout','finishOnKey','numDigits'],
				Action = verb['Attr']['action']	if 'Attr' in verb and 'action' in verb['Attr'] else None
				Method = verb['Attr']['method'] if 'Attr' in verb and 'method' in verb['Attr'] else 'POST'
				NewDoc = False
				msg+='Gather was successful.'
				if Action is None:
					Action = Twiml.Url
				if Action is not None:
					#Whether or not twiml parsed, the twiml dictionary, and any error messages
					#logging.info('Getting new twiml doc')
					Valid, Twiml, AddMessage = get_external_twiml(Account, Action, Method, ModelInstance,{'Digits':str(Input)} , Twiml)
				msg += AddMessage
				if NewDoc:
					msg+='A new Twiml document was created, processing will continue on that document\n'
					return msg, True, Twiml
				else:
					msg += '\nUnable to grab new twiml document, will continue parsing'
					return msg, False, False

#the verb node of the tiwml document, the twiml document, and the instance that caused the creation of the twiml document
def process_sms(verb, OTwiml, Instance):
	msg = ''
	To = verb['Attr']['to'] if 'Attr' in verb and 'to' in verb['Attr'] else Instance.From
	From = verb['Attr']['from'] if 'Attr' in verb and 'from' in verb['Attr'] else Instance.To
	Action = verb['Attr']['action']	if 'Attr' in verb and 'action' in verb['Attr'] else None
	Method = verb['Attr']['method'] if 'Attr' in verb and 'method' in verb['Attr'] else 'POST'
	statusCallback = verb['Attr']['statusCallback'] if 'Attr' in verb and 'statusCallback' in verb['Attr'] else None

	Message,Valid,TwilioCode,TwilioMsg = messages.Message.new(
		AccountSid = Instance.AccountSid,
		request = None,
		To = To,
		From = From,
		StatusCallback = statusCallback,
		Direction = 'outbound-reply' if Instance.Sid[0:2] == 'SM' else 'outbound-call',
		Status = 'queued'
	)
	#logging.info(str(Valid)+' '+TwilioMsg)
	Message.put()

	msg += 'SMS sent to '+To+' from '+From+' with body "'+process_text(verb)+'"\n'

	Account = accounts.Account.all().filter('Sid =',Instance.AccountSid).get()
	NewDoc = False
	if Action is None:
		#then techincally we should rerequest the original url
		#but i dont make sure the method is the same :/
		#Action = OTwiml.Url
		pass
	if Action is not None:
		Valid, Twiml, AddMessage = get_external_twiml(Account, Action, Method, Instance,{'SmsSid' : Instance.Sid, 'SmsStatus' : Message.Status}, OTwiml)
	
	msg+=AddMessage

	Message.send()
	if Message.StatusCallback is not None:
		queued = Message.queueCallback()
	if Valid:
		msg+='A new Twiml document was created, processing will continue on that document'
		return msg, True, Twiml
	else:
		return msg,False,False

def process_dial(verb, OrigionalTwiml, Instance):
	if Input == '':
		if len(verb['Children']):
			msg = 'Dialing, nested elements to follow'
			for node in verb['Children']:
				response, Break, newTwiml = process_verb(node, Twiml, ModelInstance, '')
				msg += response + '\n'
				if Break:
					break
			return msg, True, False
		else:
			msg = 'DIAL SHOULD HAVE CHILDREN, NOT SURE HOW WE GOT HERE'
			return msg, True, False
	else:
		pass

def process_number(verb):
	msg = 'Dialing number: '+ process_text(verb)
	if 'sendDigits' in verb['Attr']:
		msg+='\nSending digits: '+verb['Attr']['sendDigits']
	if 'url' in verb['Attr']:
		pass
		#need to grab this twiml document, create a new call and pass in a bunch of other things, damn this gets much more complex to maintain state for, not impossible, but certainly harder and more trees
	return 

def process_conference(verb):
	return 'Putting into conference room: '+process_text(verb)

def process_hangup(verb):
	return 'Call Hung Up'

def process_redirect(verb, OTwiml, Instance):
	msg = 'Redirecting to '+process_text(verb)
	Account = accounts.Account.all().filter('Sid =',Instance.AccountSid).get()
	NewDoc = False
	Valid, Twiml, AddMessage = get_external_twiml(Account,process_text(verb),verb['Attr']['method'] if 'method' in verb['Attr'] else 'POST', Instance, {}, OTwiml)
	msg+=AddMessage
	if Valid:
		msg+='A new Twiml document was created, processing will continue on that document'
		return msg, True, Twiml
	else:
		return msg,False,False

def process_reject(verb):
	if 'Attr' in verb and 'reason' in verb['Attr']:
		return 'Call rejected, reason: '+verb['Attr']['reason']
	else:
		return 'Call rejected, reason: rejected'

def process_text(verb):
	#logging.info('process text')
	if 'Data' in verb['Children'][0]:
		return verb['Children'][0]['Data']
	else:
		return ''

#this not ideal, but was getting errors other ways so will refactor when needed.
#returns the text, whether or not it should stop processing and wait for input and the new twiml document, if applicable
def process_verb(verb,Twiml, ModelInstance, Input):
	#logging.info(verb)
	if verb['Type'] =='Say': 
		return process_say(verb) #done
	elif verb['Type'] == 'Play': 
		return process_play(verb) #done
	elif verb['Type'] == 'Record': 
		return process_record(verb, Twiml, ModelInstance, Input) #done
	elif verb['Type'] == 'Gather':
		return process_gather(verb, Twiml, ModelInstance, Input)
	elif verb['Type'] == 'Sms':
		return process_sms(verb, Twiml, ModelInstance) #done
	elif verb['Type'] == 'Dial':
		return (process_dial(verb),True,False)
	elif verb['Type'] == 'Number':
		return (process_number(verb),False,False)
	elif verb['Type'] == 'Conference':
		return (process_conference(verb),False,False)
	elif verb['Type'] == 'Hangup':
		return (process_hangup(verb),True,False) #done
	elif verb['Type'] == 'Redirect':
		return (process_redirect(verb, Twiml, ModelInstance),True,False) #done
	elif verb['Type'] == 'Reject':
		return (process_reject(verb),True,False) #done
	elif verb['Type'] == 'Pause':
		return process_pause(verb) #done
	elif verb['Type'] == 'Text':
		return (process_text(verb),False,False) #done
			
#Returns Whether or not it went well, The new Twiml model instance, and messsages
def get_external_twiml(Account, Action, Method, Instance, Payload, Twiml):
	msg = ''
	#determine if its a relative or absolute URL
	OriginalUrl = urlparse.urlparse(Twiml.Url)
	NewUrl = urlparse.urlparse(Action)
	
	if NewUrl.scheme != '' and NewUrl.netloc != '':
		ActionUrl= Action
	else:
		ActionUrl = OriginalUrl.scheme+OriginalUrl.netloc+'/'+Action

	Response = request.request_twiml(Account, ActionUrl, Method, Payload)		#make call to action with smssid and status, with correct method
	if 200 <= Response.status_code <= 300:
		#YAY WE HAVE AN ACTUAL URL!
		#get the new twiml document
		#parse the new twiml document
		if 'Content-Length' in Response.headers and Response.headers['Content-Length'] > 0:
			#return Valid, Twiml_object, ErrorMessage
			Valid, Twiml_object, TwilioCode, TwilioMsg =  parse_twiml(Response.content, True if Instance.Sid[0:2] == 'SM' else False) #returns Valid, Twiml_object, ErrorMessage
			Twiml = None
			if Valid:
				#if all that works, create new twiml document
				CallSid = Instance.Sid if Instance.Sid[0:2] == 'CA' else None
				SmsSid = Instance.Sid if Instance.Sid[0:2] == 'SM' else None
				Twiml, Valid, TwilioCode,TwilioMsg = twimls.Twiml.new(
					AccountSid = Account.Sid,
					Url = Action,
					request = None,
					Twiml = pickle.dumps(Twiml_object),
					Current = [],
					SmsSid = SmsSid,
					CallSid = CallSid
				)
				Twiml.put()
			else:
				msg+='An error occurred parsing your action\'s Twiml document, will continue parsing original\n'+TwilioMsg+'\n'
			return Valid, Twiml, msg

	return False, False, 'Could not retrieve a valid TwiML document'