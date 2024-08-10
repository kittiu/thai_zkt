import frappe
from urllib.parse import parse_qs, urlparse
import thai_zkt.www.iclock.local_config as config
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.service as service
import thai_zkt.www.iclock.push_protocol_2 as push2
import thai_zkt.www.iclock.push_protocol_3 as push3
import json

no_cache = 1

device_punch_values_IN = getattr(config, 'device_punch_values_IN', [0,4])
device_punch_values_OUT = getattr(config, 'device_punch_values_OUT', [1,5])

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
	print("Serial Number:",serial_number)
     
	if request.method == 'GET':
		options = utils.get_arg(args,'options')
		language = utils.get_arg(args,'language')
		pushver = utils.get_arg(args,'pushver')
		pushflag = utils.get_arg(args,'PushOptionsFlag')
  
		print("Options:",options)
		print("Language:",language)
		print("Push Ver:",pushver)
		print("Push Options Flag:",pushflag)
  
		info = {
			"PushVersion":pushver
		}
  
		ret_msg = service.update_terminal_info(serial_number, info)
		print("update_terminal_info:ret_msg:",ret_msg)

		data = request.get_data(True,True)
		print("data:",data)
  
		if pushver.startswith("2"):
			ret_msg = push2.handle_cdata_get(args)
		else:
			ret_msg = push3.handle_cdata_get(args)



	else: # request.method == "POST"
		table = utils.get_arg(args,'table')
		stamp = utils.get_arg(args,'Stamp')
		opstamp = utils.get_arg(args,'OpStamp')

		print("Table:",table)
		print("Stamp:",stamp)
		print("OpStamp:",opstamp)

		data = request.get_data(True,True)
		print("data:",data)

		if table == "options":

			code, terminal = service.get_terminal(serial_number)
			print("terminal.push_version:",terminal["push_version"])

			if terminal["push_version"].startswith("3"):
				push3.handle_querydata_post_options(serial_number, data)
			else:
				push2.handle_querydata_post_options(serial_number, data)

		elif table == "ATTLOG": # push protocol v.2

			push2.handle_cdata_post_attlog(serial_number, data) # attendance

		elif table == "OPERLOG": # push protocol v.2

			is_main = service.is_main_terminal(serial_number)
			ret_msg = push2.handle_cdata_post_operlog(is_main, data) # user & bio photo

		elif table == "BIODATA": # push protocol v.2

			is_main = service.is_main_terminal(serial_number)
			ret_msg = push2.handle_cdata_post_biodata(is_main, data) # bio data

		elif table == "rtlog": # push protocol v.3

			push3.handle_cdata_post_rtlog(serial_number, data) # attendance
      
		elif table == "tabledata": # push protocol v.3
	
			is_main = service.is_main_terminal(serial_number)

			tablename = utils.get_arg(args,'tablename')

			if tablename == "user":
				ret_msg = push3.handle_querydata_post_tabledata_user(is_main, data)
			elif tablename == "biodata":
				ret_msg = push3.handle_querydata_post_tabledata_biodata(is_main, data)
			elif tablename == "biophoto":
				ret_msg = push3.handle_querydata_post_tabledata_biophoto(is_main, data)

		else:

			lines = data.split("\n")
			print("lines:",lines)

			for line in lines:
				words = line.split("\t")
				print("words:",words)



	print("RETURN:",ret_msg)
	context.ret_msg = ret_msg
	return context