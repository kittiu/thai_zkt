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
		devicetype = utils.get_arg(args,'DeviceType')
  
		print("Options:",options)
		print("Language:",language)
		print("Push Ver:",pushver)
		print("Push Options Flag:",pushflag)
		print("Device Type:",devicetype)
  
		info = {
			"PushVersion":pushver,
			"DeviceType":devicetype
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

			erpnext_status_code, erpnext_message = service.get_terminal(serial_number)
			if erpnext_status_code == 200:
				terminal = erpnext_message
				device_id = terminal["alias"]
				print("Alias:",device_id)
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

			lines = data.split("\n")
			print("lines:",lines)

			item_cnt = 0
   
			for line in lines:
				words = line.split("\t")
				print("words:",words)

				if words[0].startswith("USER"):
					kv = words[0].split("=")
					user_id = kv[1]
					pin = kv[1]
					kv = words[1].split("=")
					user_name = kv[1]
					kv = words[2].split("=")
					user_pri = kv[1]
					kv = words[3].split("=")
					user_password = kv[1]
					kv = words[5].split("=")
					user_grp = kv[1]
     
					erpnext_status_code, erpnext_message = service.create_user(pin, user_name, user_pri, user_password, user_grp, user_id)
					if erpnext_status_code == 200:
						item_cnt += 1
      
				elif words[0].startswith("BIOPHOTO"):
					kv = words[0].split("=")
					pin = kv[1]
					kv = words[1].split("=")
					no = kv[1]
					kv = words[2].split("=")
					index = kv[1]
					kv = words[3].split("=")
					file_name = kv[1]
					kv = words[4].split("=")
					type = kv[1]
					kv = words[5].split("=")
					size = kv[1]
					content = words[6][8:]
     
					erpnext_status_code, erpnext_message = service.create_bio_photo(pin, type, no, index, file_name, size, content)
					if erpnext_status_code == 200:
						item_cnt += 1
					

			if item_cnt > 0:
				ret_msg = "OK:" + str(item_cnt) + "\n"




		elif table == "BIODATA":

			lines = data.split("\n")
			print("lines:",lines)

			template_cnt = 0
   
			for line in lines:
				words = line.split("\t")
				print("words:",words)
    
				if words[0].startswith("BIODATA"):
					kv = words[0].split("=")
					zk_user = kv[1]
					kv = words[1].split("=")
					no = kv[1]
					kv = words[2].split("=")
					index = kv[1]
					kv = words[3].split("=")
					valid = kv[1]
					kv = words[5].split("=")
					type = kv[1]
					kv = words[6].split("=")
					major_version = kv[1]
					kv = words[7].split("=")
					minor_version = kv[1]
					kv = words[8].split("=")
					format = kv[1]
					kv = words[9].split("=")
					template = kv[1]

					erpnext_status_code, erpnext_message = service.create_bio_data(zk_user, type, no, index, valid, format, major_version, minor_version, template)
					if erpnext_status_code == 200:
						template_cnt += 1

			if template_cnt > 0:
				ret_msg = "OK:" + str(template_cnt) + "\n"

		elif table == "rtlog":

			words = data.split("\t")
			print("words:",words)
   
			device_attendance_log = {}
   
			kv = words[0].split("=")
			device_attendance_log["timestamp"] = utils.safe_convert_date(kv[1], "%Y-%m-%d %H:%M:%S")
			kv = words[1].split("=")
			device_attendance_log["user_id"] = kv[1]
			kv = words[3].split("=")
			eventaddr = kv[1]
			kv = words[4].split("=")
			event = kv[1]
			kv = words[5].split("=")
			device_attendance_log["punch"] = kv[1]
			kv = words[6].split("=")
			verifytype = kv[1]
			kv = words[7].split("=")
			index = kv[1]

			device_attendance_log["uid"] = "0"
			device_attendance_log["status"] = "0"

			if event == "0":
   
				erpnext_status_code, erpnext_message = service.get_terminal(serial_number)
				if erpnext_status_code == 200:
					terminal = erpnext_message
					device_id = terminal["alias"]
					print("Alias:",device_id)
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

				print("before setup log")
				attendance_success_log_file = '_'.join(["attendance_success_log", device_id])
				attendance_failed_log_file = '_'.join(["attendance_failed_log", device_id])
				attendance_success_logger = service.setup_logger(attendance_success_log_file, '/'.join([config.LOGS_DIRECTORY, attendance_success_log_file])+'.log')
				attendance_failed_logger = service.setup_logger(attendance_failed_log_file, '/'.join([config.LOGS_DIRECTORY, attendance_failed_log_file])+'.log')
				print("after setup log")

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
      
		else:

			lines = data.split("\n")
			print("lines:",lines)

			for line in lines:
				words = line.split("\t")
				print("words:",words)



	print("RETURN:",ret_msg)
	context.ret_msg = ret_msg
	return context