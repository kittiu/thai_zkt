from asyncio.log import logger
import frappe
from urllib.parse import urlparse, parse_qs
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.service as service
import json

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
				if line.startswith("ID"):
					post_args = parse_qs(line)
					print(f"post_args {ldx}:", post_args)
     
					# update ZK Command Status to 'Done'
					p_id = utils.get_arg(post_args,'ID')
					p_ret_code = utils.get_arg(post_args,'Return')
					p_cmd = utils.get_arg(post_args,'CMD')

					#set ZK Command Status to 'Done'
					erpnext_status_code, erpnext_message = service.update_command_status(p_id, "Done")
					try:
						if erpnext_status_code == 200:
							ret_msg = "OK"
       
							erpnext_status_code, erpnext_message = service.get_command(p_id)
							if erpnext_status_code == 200:
								command = erpnext_message
								if command.get('after_done'):
									after_done = json.loads(command.get('after_done'))
									if after_done["action"] == "update_sync_terminal":
										erpnext_status_code, erpnext_message = service.update_sync_terminal(after_done["pin"], serial_number)
       
						elif erpnext_status_code == 404:
							ret_msg = "ERR:Command '" + p_id + "' does not exist!"
						else:
							ret_msg = "Err:" + str(erpnext_status_code) + ":" + erpnext_message
					except frappe.DoesNotExistError:
						ret_msg = "ERR:Command '" + p_id + "' does not exist!"
					except Exception as e:
						logger.exception('ERR:' + str(e))
						ret_msg = "ERROR"

				else:
					words = line.split("=")
					info[words[0]] = words[1]

		# process args and data
		print("info:", info)
		ret_msg = service.update_terminal_info(serial_number, info)
	
	# send msg back to terminal
	print("RETURN:",ret_msg)
	context.ret_msg = ret_msg
	return context
