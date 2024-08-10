# Push V.3
from asyncio.log import logger
import frappe
from urllib.parse import urlparse, parse_qs
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.service as service

no_cache = 1

def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosempgrep
	context = frappe._dict()
	context.csrf_token = csrf_token

	request = frappe.local.request

	print("---> request:",request)

	parsed_url = urlparse(request.url)
	args = parse_qs(parsed_url.query)

	print("args:",args)

	ret_msg = "OK"

	serial_number = utils.get_arg(args,'SN')
	print("/registry Serial Number:",serial_number)

	if request.method == 'POST':
		data = request.get_data(True,True)
		print("data:",data)

		# parse 'POST' args and data
		lines = data.split(",")
		#print("lines:",lines)
		
		info = {}
		post_args = None

		for ldx, line in enumerate(lines):
			if len(line)>0:
				words = line.split("=")
				info[words[0]] = words[1]

		info.pop('PushVersion', None);
		print("post_args:", post_args)
		print("info:", info)

		# process args and data
		ret_msg = service.update_terminal_info(serial_number, info) # Generate ZK Terminal.Registry Code
		if ret_msg == "OK":
			ret_msg = service.set_terminal_options(serial_number, data)

		if ret_msg == "OK":
			status_code, message = service.get_terminal(serial_number)
			if status_code == 200:
				terminal = message
				ret_msg = "RegistryCode=" + terminal["registry_code"]
	
	# send msg back to terminal
	print(">>>> RETURN:",ret_msg)
	context.ret_msg = ret_msg
	return context
