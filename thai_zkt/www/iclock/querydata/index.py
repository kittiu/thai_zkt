# Push V.3
import frappe
import json
from urllib.parse import urlparse, parse_qs
import thai_zkt.www.iclock.service as service
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.push_protocol_3 as push3

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
	print("/querydata Serial Number:",serial_number)
 
	data = request.get_data(True,True)
	print("data:",data)
 
	if request.method == 'POST':
     
		type = utils.get_arg(args,'type')

		# ZK Terminal Form : Direct Command : Get Info
		# or Terminal send itself
		if type == "options":
			ret_msg = push3.handle_querydata_post_options(serial_number,data)

		# ZK Terminal Form : Direct Command : Get User
		elif type == "tabledata":
			is_main = service.is_main_terminal(serial_number)

			tablename = utils.get_arg(args,'tablename')

			if tablename == "user":
				ret_msg = push3.handle_querydata_post_tabledata_user(is_main, data)
			elif tablename == "biodata":
				ret_msg = push3.handle_querydata_post_tabledata_biodata(is_main, data)
			elif tablename == "biophoto":
				ret_msg = push3.handle_querydata_post_tabledata_biophoto(is_main, data)

		# ZK Terminal Form : Direct Comamnd : Compare With Server
		# Compare Record Count in Terminal Tables (User, Bio Data, Bio Photo)
		elif type == "count":
			tablename = utils.get_arg(args,'tablename')
			cmd_id = utils.get_arg(args,'cmdid')

			if tablename in ["user","biodata","biophoto"]:
				push3.handle_querydata_post_count_table(data, tablename, cmd_id)

			service.update_compare_screen(serial_number)	

	# send msg back to terminal
	print(">>>> RETURN:",ret_msg)
	context.ret_msg = ret_msg
	return context
