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
import sys, signal, os
import urllib, urllib2
import urlparse
from StringIO import StringIO
from threading import Timer
from optparse import OptionParser
from datetime import datetime

from xml.dom import minidom
from google.appengine.api import urlfetch

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
		self.line = self.doc.split("\n")[self.lineno-2]
		
	def __str__(self):
		return "TwiMLSyntaxError at line %i col %i near %s" \
			% (self.lineno, self.col, self.line)

#Returns valid, twiml_object, error message
def parse_twiml(response):
	try:
		rdoc = minidom.parseString(response)
	except ExpatError, e:
		return False, False, TwiMLSyntaxError(e.lineno, e.offset, response)

	try:
		respNode = rdoc.getElementsByTagName('Response')[0]
	except IndexError, e:
		return False, False, 'No response tag in TwiML'

	return True, respNode, ''
	
	
