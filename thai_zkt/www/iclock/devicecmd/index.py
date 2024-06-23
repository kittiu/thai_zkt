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

	parsed_url = urlparse(request.url)
	args = parse_qs(parsed_url.query)

	print("args:",args)

	ret_msg = "OK"

	serialNumber = args.get('SN')
	print("/devicecmd Serial Number:",serialNumber)

	if request.method == 'POST':
		ret_msg = "ID=10&Return=0&CMD=CHECK"

	context.ret_msg = ret_msg

	return context

