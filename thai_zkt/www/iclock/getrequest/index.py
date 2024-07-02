import frappe
from asyncio.log import logger
from urllib.parse import urlparse, parse_qs
import thai_zkt.www.iclock.local_config as config
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

	if request.method == 'GET':
		# get arguments
		serial_number = utils.get_arg(args,'SN')
		info = utils.get_arg(args,'INFO')

		print("Serial Number:",serial_number)
		print("Info:",info)

		data = request.get_data(True,True)
		print("data:",data)

		if info == "":
			# check ZK Command DocType
			ret_msg = get_command(serial_number)
    
	else:
		data = request.get_data(True,True)
		print("data:",data)

	print(">>> RETURN:",ret_msg)
	context.ret_msg = ret_msg
	return context


def get_command(serial_number):

	ret_msg = "OK"

	dt_ZKCommand = frappe.qb.DocType('ZK Command')
	cmds = (
		frappe.qb.from_(dt_ZKCommand)
			.select(dt_ZKCommand.name, dt_ZKCommand.command)
			.where(dt_ZKCommand.terminal == serial_number)
			.where(dt_ZKCommand.status == "Create")
	).run(as_dict=True)

	print("cmds:",cmds)

	cmd_id = None
	for d_ZKCommand in cmds:
		cmd_id = d_ZKCommand.name
		print("ZK Command.id:",cmd_id,",",d_ZKCommand.command)
  
		if d_ZKCommand.command.startswith("_"):
			ret_msg = get_special_command(serial_number, cmd_id, d_ZKCommand.command)

		#set ZK Command status to 'Sent'
		erpnext_status_code, erpnext_message = service.update_command_status(cmd_id, "Sent")
		try:
			if erpnext_status_code == 200:
				if ret_msg=="OK":
					ret_msg = 'C:' + str(cmd_id) + ':' + d_ZKCommand.command + '\n'
			elif erpnext_status_code == 404:
				ret_msg = "ERR:Command '" + cmd_id + "' does not exist!"
			else:
				ret_msg = "Err:" + str(erpnext_status_code) + ":" + erpnext_message
		except frappe.DoesNotExistError:
			ret_msg = "ERR:Command '" + cmd_id + "' does not exist!"
		except Exception as e:
			logger.exception('ERR:' + str(e))
			ret_msg = "ERROR"

	return ret_msg


def get_special_command(serial_number, cmd_id, cmd):
    
	ret_msg = "OK"
    
	if cmd == "_UPDATE":
		# loop ZK User
		#   create new command 'UPDATE USERINFO'
		#   if exists ZK Bio Data
		#     create new command 'UPDATE BIODATA'
  
		erpnext_status_code, erpnext_message = service.list_user()
		try:
			if erpnext_status_code == 200:
       
				print("erpnext_message:", erpnext_message)
				users = erpnext_message
    
				if len(users) > 0:
					ret_msg = ""
    
				for user in users:
					cmd_line = 'DATA UPDATE USERINFO ' + get_user_info(user)
					new_cmd_id = service.create_command(serial_number, cmd_line, 'Sent')
					
					ret_msg += 'C:' + str(new_cmd_id) + ':' + cmd_line + '\n'
    
			elif erpnext_status_code == 404:
				ret_msg = "ERR:ZK User '" + cmd_id + "' does not exist!"
			else:
				ret_msg = "Err:" + str(erpnext_status_code) + ":" + erpnext_message
		except frappe.DoesNotExistError:
			ret_msg = "ERR:ZK User '" + cmd_id + "' does not exist!"
		except Exception as e:
			logger.exception('ERR:' + str(e))
			ret_msg = "ERROR"
    
	return ret_msg



def get_user_info(user):
    
    user_info = "\t".join(["PIN=1" + user["id"]
                           ,"Name=" + user["user_name"]
                           ,"Pri=" + user["privilege"]
                           ,"Passwd=" + user["password"]
                           ,"Card="
                           ,""
                           ,"Grp=" + user["group"]
                           ,"Verify=0"
                           ])
    
    return user_info