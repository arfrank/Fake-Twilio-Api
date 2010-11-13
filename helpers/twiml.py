#ADAPTED FROM https://github.com/minddog/twilio-emulator
"""
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
"""
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
	def __init__(self, lineno, col, doc):
		self.lineno = lineno
		self.col = col
		self.doc = doc

	def __str__(self):
		return "TwiMLSyntaxError at line %i col %i near %s" \
			% (self.lineno, self.col, self.doc)

#Returns valid, twiml_object, error message
def parse_twiml(response, sms = False):
	try:
		rdoc = minidom.parseString(response)
	except ExpatError, e:
		return False, False, 'Bad TwiML Document'

	try:
		respNode = rdoc.getElementsByTagName('Response')[0]
	except IndexError, e:
		return False, False, 'No response tag in TwiML'

	if not respNode.hasChildNodes():
		return False, False, 'No child nodes, nothing to do.'
	nodes = respNode.childNodes
	try:
		twiml_object = walk_tree(nodes,'Response', sms)
	except TwiMLSyntaxError, e:
		return False, False, e
	#lets walk the tree and create a list [ { 'Verb' : '', 'Attr': { 'action' : '', 'Method' : 'POST' } } ]
	else:
		return True, twiml_object, False

def retrieve_attr(node, Type, sms = False):
	d = {}
	for attr in node.attributes.items():
		if (sms == False and attr[0] in ALLOWED_VOICE_ELEMENTS[Type]) or (sms == True and attr[0] in ALLOWED_SMS_ELEMENTS[Type]):
			d[attr[0]] = attr[1]
		else:
			raise TwiMLSyntaxError(0, 0, 'Invalid attribute in '+Type+':('+attr[0]+'='+attr[1]+')')
	return d

def walk_tree(nodes, parentType, sms = False):
	twiml = []
	count = 0
	for node in nodes:
		if node.nodeType == node.ELEMENT_NODE:
			#If its an element, makes 
			logging.info(parentType)
			logging.info(node.nodeName.encode('ascii'))
			logging.info(sms)
			if ( ( parentType == 'Response' and ( ( node.nodeName.encode('ascii') in ALLOWED_SMS_ELEMENTS and sms == True) or (node.nodeName.encode('ascii') in ALLOWED_VOICE_ELEMENTS and sms == False) ) ) or ( parentType in ALLOWED_SUBELEMENTS ) ):
				if parentType == 'Response' or  node.nodeName.encode('ascii') in ALLOWED_SUBELEMENTS[parentType]:
					twiml.append( { 'Type' : node.nodeName.encode( 'ascii' ), 'Attr' : retrieve_attr(node, node.nodeName.encode('ascii'), sms),'Children': walk_tree(node.childNodes, node.nodeName.encode('ascii'), sms) } )
				else:
					raise TwiMLSyntaxError(0, 0, 'Invalid TwiML nested element in '+parentType+'. Not allowed to nest '+node.nodeName.encode('ascii'))					
			else:
				raise TwiMLSyntaxError(0, 0, 'Invalid TwiML in '+parentType+'. Problem with '+node.nodeName.encode('ascii')+' element: '+str(count))
		elif node.nodeType == node.TEXT_NODE and parentType != 'Response':
			if node.nodeValue.encode('ascii') != '\n':
				twiml.append( { 'Type' : 'Text', 'Data': node.nodeValue.encode('ascii') })
		count +=1
		
	return twiml



#############################################################################################



def process_say(verb):
	logging.info('process say')
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
		error = True
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
			logging.info('process record')
			msg += 'A recording has been made\n'
			if Valid:
				Action = verb['Attr']['action']	if 'Attr' in verb and 'action' in verb['Attr'] else None
				Method = verb['Attr']['method'] if 'Attr' in verb and 'method' in verb['Attr'] else 'POST'
				if Action is None:
					Action = Twiml.Url
				NewDoc = False
				if Action is not None:
					#Whether or not twiml parsed, the twiml dictionary, and any error messages
					Valid, Twiml, AddMessage = get_external_twiml(Account, Action, Method, MethodInstance, {'SmsSid' : Instance.Sid, 'SmsStatus' : Message.Status}, OTwiml)
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
		msg += 'Please enter how long you would like the recording to be'
		if error:
			msg += 'We had trouble understanding your response, please try again'
		return (msg,True,False)

def process_pause(verb):
	logging.info('process pause')
	if 'Attr' in verb and 'length' in verb['Attr']:
		return ('Pausing for '+verb['Attr']['length']+' seconds',False,False)
	else:
		return ('Pausing for 1 second',False,False)

def process_gather(verb, Twiml, ModelInstance):
	if len(verb['Children']):
		all_resp = ''
		for node in verb['Children']:
			response, Break, newTwiml = process_verb(node, Twiml, ModelInstance, '')
			all_resp += response + '\n'
			if Break:
				break
		return all_resp,True,newTwiml


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
	logging.info(str(Valid)+' '+TwilioMsg)
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
	logging.info('process text')
	if 'Data' in verb['Children'][0]:
		return verb['Children'][0]['Data']
	else:
		return ''

def process_verb(verb,Twiml, ModelInstance, Input):
	logging.info(verb)
	if verb['Type'] =='Say': 
		return process_say(verb)
	elif verb['Type'] == 'Play': 
		return process_play(verb)
	elif verb['Type'] == 'Record': 
		return process_record(verb,Twiml,ModelInstance, Input)
	elif verb['Type'] == 'Gather':
		return process_gather(verb,Twiml,ModelInstance)
	elif verb['Type'] == 'Sms':
		return process_sms(verb, Twiml, ModelInstance)
	elif verb['Type'] == 'Dial':
		return (process_dial(verb),True,False)	
	elif verb['Type'] == 'Number':
		return (process_number(verb),True,False)
	elif verb['Type'] == 'Conference':
		return (process_conference(verb),True,False)
	elif verb['Type'] == 'Hangup':
		return (process_hangup(verb),True,False)
	elif verb['Type'] == 'Redirect':
		return (process_redirect(verb, Twiml, ModelInstance),True,False)
	elif verb['Type'] == 'Reject':
		return (process_reject(verb),True,False)
	elif verb['Type'] == 'Pause':
		return process_pause(verb)
	elif verb['Type'] == 'Text':
		return (process_text(verb),False,False)
			
"""
ALLOWED_ATTRIBUTES = {
'Say':['voice','language','loop'],
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
}"""

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
			Valid, Twiml_object, ErrorMessage =  parse_twiml(Response.content, True if Instance.Sid[0:2] == 'SM' else False) #returns Valid, Twiml_object, ErrorMessage
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
				msg+='An error occurred parsing your action\'s Twiml document, will continue parsing original\n'+ErrorMessage+'\n'
			return Valid, Twiml, msg

	return False, False, 'Could not retrieve a valid TwiML document'