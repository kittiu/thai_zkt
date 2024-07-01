import frappe
from urllib.parse import urlparse, parse_qs

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

	if request.method == 'GET':
		serialNumber = args.get('SN')
		info = args.get('INFO')

		print("Serial Number:",serialNumber)
		print("Info:",info)

		data = request.get_data(True,True)
		print("data:",data)

#            return 'C:10:CHECK\n'
    
	else:
		data = request.get_data(True,True)
		print("data:",data)

	context.ret_msg = ret_msg

	return context
