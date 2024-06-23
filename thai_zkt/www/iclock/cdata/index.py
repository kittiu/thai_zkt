import requests
import json
import frappe
from urllib.parse import parse_qs, urlparse, urlsplit


no_cache = 1

config = {
	'ERPNEXT_API_KEY':'d4033010702172e',
	'ERPNEXT_API_SECRET':'f565902002bf6ee',
	'ERPNEXT_URL':'http://dcode.com:8000',
	'ERPNEXT_VERSION':15,

	'LOGS_DIRECTORY':'logs', # logs of this script is stored in this directory
	'SERVER_PORT':8000,

	'devices':[
    {'device_id':'test_1','ip':'192.168.1.50', 'punch_direction': None, 'clear_from_device_on_fetch': False, 'serial_number':'CKII235260037'}
	],

	'shift_type_device_mapping': [
    {'shift_type_name': ['Shift1'], 'related_device_id': ['test_1']}
	],
	'allowed_exceptions': [1,2,3]
}

EMPLOYEE_NOT_FOUND_ERROR_MESSAGE = "No Employee found for the given employee field value"
EMPLOYEE_INACTIVE_ERROR_MESSAGE = "Transactions cannot be created for an Inactive Employee"
DUPLICATE_EMPLOYEE_CHECKIN_ERROR_MESSAGE = "This employee already has a log with the same timestamp"
allowlisted_errors = [EMPLOYEE_NOT_FOUND_ERROR_MESSAGE, EMPLOYEE_INACTIVE_ERROR_MESSAGE, DUPLICATE_EMPLOYEE_CHECKIN_ERROR_MESSAGE]

if hasattr(config,'allowed_exceptions'):
    allowlisted_errors_temp = []
    for error_number in config.allowed_exceptions:
        allowlisted_errors_temp.append(allowlisted_errors[error_number-1])
    allowlisted_errors = allowlisted_errors_temp

device_punch_values_IN = getattr(config, 'device_punch_values_IN', [0,4])
device_punch_values_OUT = getattr(config, 'device_punch_values_OUT', [1,5])
ERPNEXT_VERSION = getattr(config, 'ERPNEXT_VERSION', 14)

def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosempgrep
	context = frappe._dict()
	context.csrf_token = csrf_token
	request = frappe.local.request

	print("---> request:",dir(request))

	parsed_url = urlparse(request.url)
	args = parse_qs(parsed_url.query)

	print("args:",args)

	ret_msg = "OK"
	serialNumber = args.get('SN')
	print("Serial Number:",serialNumber)
     
	if request.method == 'GET':
		options = args.get('options')
		language = args.get('language')
		pushver = args.get('pushver')
		pushflag = args.get('PushOptionsFlag')
          
		print("Options:",options)
		print("Language:",language)
		print("Push Ver:",pushver)
		print("Push Options Flag:",pushflag)

	else:
          
		table = args.get('table')
		stamp = args.get('Stamp')
		opstamp = args.get('OpStamp')

		print("Table:",table)
		print("Stamp:",stamp)
		print("OpStamp:",opstamp)

		data = request.get_data(True,True)
		print("data:",data)

		if table == "options":
			words = data.decode('utf-8').split(",")
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
							log['timestamp'] = _safe_convert_date(word, "%Y-%m-%d %H:%M:%S")
						elif idx == 2:
							log['punch'] = int(word)
						elif idx == 3:
							log['status'] = int(word)
					logs.append(log)

			device_id = get_device_id(serialNumber)

			for device_attendance_log in logs:
				print("attendance:",device_attendance_log)
				punch_direction = None

				erpnext_status_code, erpnext_message = send_to_erpnext(device_attendance_log['user_id'], device_attendance_log['timestamp'], device_id, punch_direction)
				if erpnext_status_code == 200:
					print("\t".join([erpnext_message, str(device_attendance_log['uid']),
                        str(device_attendance_log['user_id']), str(device_attendance_log['timestamp'].timestamp()),
                        str(device_attendance_log['punch']), str(device_attendance_log['status']),
                        json.dumps(device_attendance_log, default=str)]))
				else:
					print("\t".join([str(erpnext_status_code), str(device_attendance_log['uid']),
                        str(device_attendance_log['user_id']), str(device_attendance_log['timestamp'].timestamp()),
                        str(device_attendance_log['punch']), str(device_attendance_log['status']),
                        json.dumps(device_attendance_log, default=str)]))
					if not(any(error in erpnext_message for error in allowlisted_errors)):
						raise Exception('API Call to ERPNext Failed.')
		elif table == "OPERLOG":
			
			lines = data.split("\n")
			print("lines:",lines)

			for line in lines:
				words = line.split("\t")
				print("words:",words)

		else:
                
			lines = data.split("\n")
			print("lines:",lines)

			for line in lines:
				words = line.split("\t")
				print("words:",words)

	context.ret_msg = ret_msg

	return context


def send_to_erpnext(employee_field_value, timestamp, device_id=None, log_type=None):
    """
    Example: send_to_erpnext('12349',datetime.datetime.now(),'HO1','IN')
    """
    endpoint_app = "hrms" if ERPNEXT_VERSION > 13 else "erpnext"
    url = f"{config.ERPNEXT_URL}/api/method/{endpoint_app}.hr.doctype.employee_checkin.employee_checkin.add_log_based_on_employee_field"
    headers = {
        'Authorization': "token "+ config.ERPNEXT_API_KEY + ":" + config.ERPNEXT_API_SECRET,
        'Accept': 'application/json'
    }
    data = {
        'employee_field_value' : employee_field_value,
        'timestamp' : timestamp.__str__(),
        'device_id' : device_id,
        'log_type' : log_type
    }
    response = requests.request("POST", url, headers=headers, json=data)
    if response.status_code == 200:
        return 200, json.loads(response._content)['message']['name']
    else:
        error_str = _safe_get_error_str(response)
        if EMPLOYEE_NOT_FOUND_ERROR_MESSAGE in error_str:
            print('\t'.join(['Error during ERPNext API Call.', str(employee_field_value), str(timestamp.timestamp()), str(device_id), str(log_type), error_str]))
        else:
            print('\t'.join(['Error during ERPNext API Call.', str(employee_field_value), str(timestamp.timestamp()), str(device_id), str(log_type), error_str]))
        return response.status_code, error_str

def _safe_convert_date(datestring, pattern):
    try:
        print("_safe_convert_date("+datestring+" , "+pattern+")")
        return datetime.datetime.strptime(datestring, pattern)
    except:
        print("_safe_convert_date(None)")
        return None
    
def get_device_id(serial_number):

    result = serial_number

    for device in config.devices:
        if device['serial_number'] == serial_number:
            result = device['device_id']
            break

    return result

def _safe_get_error_str(res):
    try:
        error_json = json.loads(res._content)
        if 'exc' in error_json: # this means traceback is available
            error_str = json.loads(error_json['exc'])[0]
        else:
            error_str = json.dumps(error_json)
    except:
        error_str = str(res.__dict__)
    return error_str