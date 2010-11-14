Fake Twilio API

Disclaimer: This project is in no way Authorized or supported by Twilio Inc. http://www.twilio.com

===============

1. Whats this about?
--------------------

This is an attempt to replicate the Twilio API in order to create a way to test locally, or deploy to GAE and test a lot of basic functionality for free.

A semi-recent deployed version can be found at <a href="https://twilioapi.appspot.com/">https://twilioapi.appspot.com/</a>

2. What has been done?
----------------------
- A basic outline of how the API works
- SMS/Messages - Posting/Listing/Retrieving via the API
- Authentication (Basic HTTP)
- Lists Handler
- TwiML processing (could be more robust, but currently works)

3. What still needs to be done(may not be accurate - in fact will definitely be out of date)?
-------------------------------
* Finish rounding out all models (including validators/santizers for each model)
	* Recordings
	* Transcriptions
	* Notifications
	* Phone Numbers
	* Calls
	* Messages
	* Accounts
* Date support for listings
* Making a Call via a Post request
* Faking Incoming Calls/SMS
* Forcing errors for testing purposes
* Validating all API calls like Twilio
* Returning proper errors
* Internationalization of phone calls
* TESTING

4. Who am I?
------------
Just someone who enjoys working with the Twilio API and wanted a different way to develop on it and one that didn't accidentally call people at 1am like I once did.

5. License (for now)
-----------
Copyright (c) 2010 Aaron Frank

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.