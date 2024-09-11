import frappe
from urllib.parse import urlparse, parse_qs
import thai_zkt.www.iclock.utils as utils

no_cache = 1

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
	print("/ping Serial Number:",serial_number)

	context.ret_msg = ret_msg

	return context
