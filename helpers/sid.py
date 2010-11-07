from hashlib import sha256
"""
Guess at what twilio uses to compute an sid
Time
Object Type
"""
def compute_sid(params_dictionary):
	hash_string  = ''
	keys = params_dictionary.items()#.sort()
	for key in keys:
		pass
#		hash_string += key + '=' + params_dictionary[key]
	return sha256(hash_string).hexdigest()