from google.appengine.ext import db
from models import base

class Account(base.CommonModel):
	Sid = db.StringProperty()
	FriendlyName = db.StringProperty()
	Status = db.StringProperty()
	AuthToken = db.StringProperty()
