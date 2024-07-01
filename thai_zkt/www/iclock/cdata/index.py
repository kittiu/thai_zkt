import frappe
from urllib.parse import parse_qs, urlparse
import thai_zkt.www.iclock.local_config as config
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.service as service
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

		data = request.get_data(True,True)
		print("data:",data)

	else:
		table = utils.get_arg(args,'table')
		stamp = utils.get_arg(args,'Stamp')
		opstamp = utils.get_arg(args,'OpStamp')

		print("Table:",table)
		print("Stamp:",stamp)
		print("OpStamp:",opstamp)

		data = request.get_data(True,True)
		print("data:",data)

		if table == "options":
			words = data.split(",")
			print("words:",words) 

            # resolve "~OEMVendor=ZKTECO CO., LTD." (Comma is inside company name)
			finalwords = []
			idx = 0

			for word in words:
				if "=" in word:
					finalwords.append(word)
					idx += 1
				else:
					finalwords[idx-1] = finalwords[idx-1] + "," + word

			for word in finalwords:
				print("  -",word)

		elif table == "ATTLOG":
			lines = data.split("\n")
			print("lines:",lines)

			logs = []

			for ldx, line in enumerate(lines):
				if len(line)>0:
					words = line.split("\t")
					log = {}
					log['uid'] = ldx
					for idx, word in enumerate(words):
						print("word:",idx,word)
						if idx == 0:
							log['user_id'] = int(word)
						elif idx == 1:
#                            log['timestamp'] = _safe_convert_date(word, "%Y-%m-%d %H:%M:%S.%f")
							log['timestamp'] = utils.safe_convert_date(word, "%Y-%m-%d %H:%M:%S")
						elif idx == 2:
							log['punch'] = int(word)
						elif idx == 3:
							log['status'] = int(word)
					logs.append(log)

			print("logs:",logs)

			device_id = service.get_device_id(serial_number)

			print("before setup log")
			attendance_success_log_file = '_'.join(["attendance_success_log", device_id])
			attendance_failed_log_file = '_'.join(["attendance_failed_log", device_id])
			attendance_success_logger = service.setup_logger(attendance_success_log_file, '/'.join([config.LOGS_DIRECTORY, attendance_success_log_file])+'.log')
			attendance_failed_logger = service.setup_logger(attendance_failed_log_file, '/'.join([config.LOGS_DIRECTORY, attendance_failed_log_file])+'.log')
			print("after setup log")

			for device_attendance_log in logs:
				print("attendance:",device_attendance_log)
				punch_direction = None
				erpnext_status_code, erpnext_message = service.create_attendance(device_attendance_log['user_id'], device_attendance_log['timestamp'], device_id, punch_direction)
				if erpnext_status_code == 200:
					print("\t".join([erpnext_message, str(device_attendance_log['uid']),
                        str(device_attendance_log['user_id']), str(device_attendance_log['timestamp'].timestamp()),
                        str(device_attendance_log['punch']), str(device_attendance_log['status']),
                        json.dumps(device_attendance_log, default=str)]))
					attendance_success_logger.info("\t".join([erpnext_message, str(device_attendance_log['uid']),
                        str(device_attendance_log['user_id']), str(device_attendance_log['timestamp'].timestamp()),
                        str(device_attendance_log['punch']), str(device_attendance_log['status']),
                        json.dumps(device_attendance_log, default=str)]))

				else:
					print("\t".join([str(erpnext_status_code), str(device_attendance_log['uid']),
                        str(device_attendance_log['user_id']), str(device_attendance_log['timestamp'].timestamp()),
                        str(device_attendance_log['punch']), str(device_attendance_log['status']),
                        json.dumps(device_attendance_log, default=str)]))
					attendance_failed_logger.error("\t".join([str(erpnext_status_code), str(device_attendance_log['uid']),
                        str(device_attendance_log['user_id']), str(device_attendance_log['timestamp'].timestamp()),
                        str(device_attendance_log['punch']), str(device_attendance_log['status']),
                        json.dumps(device_attendance_log, default=str)]))
					if not(any(error in erpnext_message for error in service.allowlisted_errors)):
						raise Exception('API Call to ERPNext Failed.')
		elif table == "OPERLOG":
			data = request.get_data(True,True)
			print("data:",data)

			lines = data.split("\n")
			print("lines:",lines)

			for line in lines:
				words = line.split("\t")
				print("words:",words)

		else:
			data = request.get_data(True,True)
			print("data:",data)

			lines = data.split("\n")
			print("lines:",lines)

			for line in lines:
				words = line.split("\t")
				print("words:",words)

	print("RETURN:",ret_msg)
	context.ret_msg = ret_msg
	return context