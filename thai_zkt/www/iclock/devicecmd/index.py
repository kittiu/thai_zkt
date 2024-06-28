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
	print("/devicecmd Serial Number:",serial_number)

	if request.method == 'POST':
		data = request.get_data(True,True)
		print("data:",data)

		# parse 'POST' args and data
		lines = data.split("\n")
		#print("lines:",lines)
		
		info = {}

		for ldx, line in enumerate(lines):
			if len(line)>0:
				if (ldx == 0): # first line is args
					post_args = parse_qs(line)
				else:
					words = line.split("=")
					info[words[0]] = words[1]

		print("post_args:", post_args)
		print("info:", info)

		# process args and data
		ret_msg = service.update_terminal_info(serial_number, post_args, info)
	
	# send msg back to terminal
	print("RETURN:",ret_msg)
	context.ret_msg = ret_msg
	return context




