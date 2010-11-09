from libraries.gaesessions import get_current_session


def check_logged_in(function):
	def wrapper_method(self, *args):
		session = get_current_session()
		if 'Account' not in session: #not hasattr(session,'account'):
			self.redirect('/login')
		else:
			self.data = {'session': session,'Account':session['Account']}
			return function(self, *args)
	return wrapper_method