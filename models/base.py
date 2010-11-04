from google.appengine.ext import db

class CommonModel(db.Expando):
	DateCreated = db.DateTimeProperty()
	DateUpdated = db.DateTimeProperty()