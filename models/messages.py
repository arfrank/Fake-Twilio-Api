from google.appengine.ext import db
from models import base

class Message(base.CommonModel):
	To = db.StringProperty()
	From = db.StringProperty()
	Body = db.StringProperty()
	DateCreated = db.StringProperty()
	DateUpdated = db.StringProperty()
	DateSent = db.StringProperty()
	AccountSid = db.StringProperty()
	__Sid = db.StringProperty()
	Status = db.StringProperty()
	Direction = db.StringProperty()
	Price = db.StringProperty()

	def __init__(To,From,Body,AccountSid,Direction,Status):
		self.To = To
		self.From = From
		self.Body = Body
		self.AccountSid = AccountSid
		self.Direction = Direction
		self.Status = Status
		self.Price = Price
		self.__Sid = self.__compute_sid()
		
	def __compute_sid():
		pass
