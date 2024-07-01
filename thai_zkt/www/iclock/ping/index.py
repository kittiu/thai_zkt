import frappe
from urllib.parse import urlsplit

no_cache = 1

def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosempgrep
	context = frappe._dict()
	context.csrf_token = csrf_token

	request = frappe.local.request

	print("---> request:",request)

	ret_msg = "OK"

	serialNumber = args.get('SN')
	print("Serial Number:",serialNumber)

	context.ret_msg = ret_msg

	return context
