Fake Twilio API
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

3. What still needs to be done?
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