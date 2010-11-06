def to_html(dictionary):
	string = ""
	for item in dictionary:
		if item.lower() == 'twilioresponse' and type(dictionary[item]) is dict:
			string += "<html><head><title>200</title></head>"+"<body class=\"twilioresponse\">"+to_html(dictionary[item])+"</body></html>"
		if type(dictionary[item]) is dict:
			string += "<div class=\""+item.lower()+"\">"+to_html(dictionary[item])+"</div>"
		elif type(dictionary[item]) is list:
			for element in dictionary[item]:
				string+="<dic class=\""+item+"\">"+to_html(element)+"</div>"
		else:
			string +='<div class="'+item.lower()+'">'+str(dictionary[item])+"</div>"
	return string


"""

<body class="twilio-response">
	<div class="recording"> 
		<div class="sid">REdbf89bba5bdebc454b0e1cf46bf6c9de</div> 
		<div class="account-sid">AC297dc81c38311ca7de9a72d48ec9b06b</div> 
		<div class="call-sid">CAef3c154aef96947e63a445e6addc6da8</div> 
		<div class="duration">5</div> 
		<div class="date-created">Mon, 01 Nov 2010 11:34:38 -0700</div> 
		<div class="date-updated">Mon, 01 Nov 2010 11:34:38 -0700</div> 
	</div>
</body> 
</html>
"""
