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
	# return 'C:10:CHECK\n'
	# return 'C:10:INFO\n'

	ret_msg = "OK"

	dt_ZKCommand = frappe.qb.DocType('ZK Command')
	cmds = (
		frappe.qb.from_(dt_ZKCommand)
			.select(dt_ZKCommand.id, dt_ZKCommand.command)
			.where(dt_ZKCommand.terminal_name == serial_number)
			.where(dt_ZKCommand.status == "Create")
	).run(as_dict=True)

	print("cmds:",cmds)

	cmd_id = 0
	for d_ZKCommand in cmds:
		cmd_id = d_ZKCommand.id
		print("ZK Command.id:",cmd_id,",",d_ZKCommand.command)

		#set ZK Command status to 'Sent'
		erpnext_status_code, erpnext_message = service.update_command_status(cmd_id, "Sent")
		try:
			if erpnext_status_code == 200:
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
