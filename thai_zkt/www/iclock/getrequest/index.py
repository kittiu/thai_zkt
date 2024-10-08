import frappe
from asyncio.log import logger
from urllib.parse import urlparse, parse_qs
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.service as service
import thai_zkt.www.iclock.push_protocol_3 as push3

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
 
	code, terminal = service.get_terminal(serial_number)

	"""
	Special Command (Prefix '_')
	"""
	dt_ZKCommand = frappe.qb.DocType('ZK Command')
	cmds = (
		frappe.qb.from_(dt_ZKCommand)
			.select(dt_ZKCommand.name, dt_ZKCommand.command)
			.where(dt_ZKCommand.terminal == serial_number)
			.where(dt_ZKCommand.status == "Create")
   			.where(dt_ZKCommand.command.like("\_%"))
			.limit(1)
	).run(as_dict=True)

	print("Special cmds:",cmds)
 
	cmd_id = None
	for d_ZKCommand in cmds:
		cmd_id = d_ZKCommand.name
		print("ZK Command.id:",cmd_id,",",d_ZKCommand.command)

		ret_msg = get_special_command(serial_number, cmd_id, d_ZKCommand.command, terminal)
  
  		#set ZK Command status to 'Sent'
		erpnext_status_code, erpnext_message = service.update_command_status(cmd_id, "Sent")
		try:
			if erpnext_status_code == 200:
				if ret_msg=="OK":
					ret_msg = 'C:' + str(cmd_id) + ':' + d_ZKCommand.command + '\n'
			elif erpnext_status_code == 404:
				ret_msg = "ERR:Command '" + cmd_id + "' does not exist!"
			else:
				ret_msg = "ERR:" + str(erpnext_status_code) + ":" + erpnext_message
		except frappe.DoesNotExistError:
			ret_msg = "ERR:Command '" + cmd_id + "' does not exist!"
		except Exception as e:
			logger.exception('ERR:' + str(e))
			ret_msg = "ERROR"

	if ret_msg != "OK":
		return ret_msg

	"""
	Normal Command
	"""
	dt_ZKCommand = frappe.qb.DocType('ZK Command')
	cmds = (
		frappe.qb.from_(dt_ZKCommand)
			.select(dt_ZKCommand.name, dt_ZKCommand.command)
			.where(dt_ZKCommand.terminal == serial_number)
			.where(dt_ZKCommand.status == "Create")
			.limit(60)
	).run(as_dict=True)

	print("Normal cmds:",cmds)
 
	cmd_id = None
	cmd_id_list = []
	for d_ZKCommand in cmds:
		cmd_id = d_ZKCommand.name
		print("ZK Command.id:",cmd_id,",",d_ZKCommand.command)
  
		if d_ZKCommand.command.startswith("_"):
			continue

		if ret_msg=="OK":
			ret_msg = ""
		ret_msg += 'C:' + str(cmd_id) + ':' + d_ZKCommand.command + '\n'

		cmd_id_list.append(cmd_id)
   
	if ret_msg=="OK":
		return ret_msg

	#set ZK Command status to 'Sent'
	erpnext_status_code, erpnext_message = service.update_command_list_status(cmd_id_list, "Sent")
	try:
		if erpnext_status_code == 200:
			print("cur:",ret_msg)
		elif erpnext_status_code == 404:
			ret_msg = "ERR:Command '" + cmd_id_list + "' does not exist!"
		else:
			ret_msg = "ERR:" + str(erpnext_status_code) + ":" + erpnext_message
	except frappe.DoesNotExistError:
		ret_msg = "ERR:Command '" + cmd_id_list + "' does not exist!"
	except Exception as e:
		logger.exception('ERR:' + str(e))
		ret_msg = "ERROR"

	return ret_msg

"""
ZK Command that starts with '_'
"""
def get_special_command(serial_number, cmd_id, cmd, terminal):
    
	ret_msg = "OK"
    
	if cmd == "_CHECK":
		ret_msg = push3.cmd_check(serial_number)
  
	elif cmd == "_GET_OPTIONS":
		ret_msg = push3.cmd_get_options(serial_number)

	return ret_msg
