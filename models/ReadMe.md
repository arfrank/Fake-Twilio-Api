Models
==============================
A basic primer on how the models work

Basic Model
-----------
* Functions
	- Properties<br>Everything has these properties
		- DateSent
		- DateCreated
		- Sid (should move to the base model, although need to define for every model separately since each model has a special prefix)
	- \_\_init\_\_
		-Avoid using this because it is a heavy function on the backend
		-
	- New
		* Class Method
	- new_Sid
		* Class Method
* Exceptions
	- Accounts
		They inherit this model, but don't have an AccountSid associated with them, so we have to check for InstanceModel type if it is and use a slightly different


-
-