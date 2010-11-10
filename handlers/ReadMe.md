Handlers
========

A primer on the handlers

------------------------
* Main Webapp (main.py)<br>
	Handles the user side
	- Registration
	- Login
	- Log Display
	- Faking Incoming Calls & SMS
* Base Handler (base_handler.py) - Everything inherits from two classes here except main webapp
	- List Handler - Just RESTful way of getting a list of objects back
		- Functions
			- \_\_init\_\_
				- InstanceModel = Query Class of the object type (ie. messages.Message.all())
				- AllowedMethods =  Allow which rest methods to allow for this type of object (ie. ['GET','POST','PUT','DELETE'])
				- AllowedFilters = For GET calls, limit what parameters can be passed in to filter the query (ie. { 'GET':[['To','='],['From','='],['DateSent','=']] })<br>Dates are currently not supported as filters
				- ListName = Plural name of the object (ie. 'SmsMessages')
				- InstanceModelName = Singular name of the object (ie. 'SmsMessage')
			- GET
				- Filters by AllowedFilters if passed in and returns a list with additional parameters PageSize & Page for pagination<br>
				Also passes back a lot of additional Uri information
			- POST
				- Typically overloaded at the object class level in order to create a new object, if that is supported
			- PUT
				- Typically unused so far
			- DELETE
				- Typically unused so far
		- TBD
			- Dates
				- Entirely unsupported as of right now, possibly simple as just trying it out, but not yet
			- Subresources
	- Instance Handler - Really just a RESTful class with filtering built in for individual objects
		- Functions
			- \_\_init\_\_
				- InstanceModel = Query Class of the object type (ie. phone_numbers.Phone_Number.all())
				- AllowedMethods = Allow which rest methods to allow for this type of object (ie. ['GET','POST','PUT','DELETE'])
				- InstanceModelName = Singular name of the object (ie. 'IncomingPhoneNumber')
				- AllowedProperties = Filter which properties can be updated view POST and PUT calls (ie. { 'POST' : ['FriendlyName','ApiVersion','VoiceUrl',..., 'PUT' : ['FriendlyName','ApiVersion','VoiceUrl',...] }
			
			- GET
				Url Path includes the type of object and the Sid of the specific object so we can pass back the correct object in the correct format
			- POST
				- If allowed will update the allowed properties of the object and return the same info as GET
			- PUT
				- If allowed will update the allowed properties of the object and return the same info as GET
			- DELETE
				- If allowed will delete the specified object and return 204 if everything goes correctly
		- TBD
			- Dates
				- Entirely unsupported as of right now, possibly simple as just trying it out, but not yet
			- Subresources