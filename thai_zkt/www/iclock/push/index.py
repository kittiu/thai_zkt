# Push V.3
import frappe
from urllib.parse import urlparse, parse_qs
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.push_protocol_3 as push3

no_cache = 1

# kittiu: This is just the test?

def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosempgrep
	context = frappe._dict()
	context.csrf_token = csrf_token

	request = frappe.local.request

	print("---> request:",request)

	ret_msg = "OK"

	parsed_url = urlparse(request.url)
	args = parse_qs(parsed_url.query)

	print("args:",args)

	serial_number = utils.get_arg(args,'SN')
	print("/push Serial Number:",serial_number)
 
	data = request.get_data(True,True)
	print("data:",data)
 
	if request.method == 'POST':
		ret_msg = push3.handle_push_post(serial_number)


	# send msg back to terminal
	print(">>>> RETURN:",ret_msg)
	context.ret_msg = ret_msg
	return context
