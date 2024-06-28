import frappe
from asyncio.log import logger
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.local_config as config
import requests
import json
import logging
import datetime
from logging.handlers import RotatingFileHandler

EMPLOYEE_NOT_FOUND_ERROR_MESSAGE = "No Employee found for the given employee field value"
EMPLOYEE_INACTIVE_ERROR_MESSAGE = "Transactions cannot be created for an Inactive Employee"
DUPLICATE_EMPLOYEE_CHECKIN_ERROR_MESSAGE = "This employee already has a log with the same timestamp"
allowlisted_errors = [EMPLOYEE_NOT_FOUND_ERROR_MESSAGE, EMPLOYEE_INACTIVE_ERROR_MESSAGE, DUPLICATE_EMPLOYEE_CHECKIN_ERROR_MESSAGE]

if hasattr(config,'allowed_exceptions'):
    allowlisted_errors_temp = []
    for error_number in config.allowed_exceptions:
        allowlisted_errors_temp.append(allowlisted_errors[error_number-1])
    allowlisted_errors = allowlisted_errors_temp

def update_command_status(cmd_id, status):
    """
    Example: update_command_status(1, "Sent")
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK Command/{cmd_id}"
    headers = utils.get_headers()

    data = {
        'status' : status
	}


    if status == "Sent":
        now = datetime.datetime.now()
        data['sent_time'] = now.__str__()
    elif status == "Done":
        now = datetime.datetime.now()
        data['done_time'] = now.__str__()

    print("data:",data)

    response = requests.request("PUT", url, headers=headers, json=data)
    if response.status_code == 200:
        print("response.content",response._content)
        return 200, json.loads(response._content)['data']['name']
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(cmd_id), str(status),  error_str]))
        return response.status_code, error_str

def update_terminal_info(serial_number, post_args, info):

    ret_msg = "OK"

    # set ZK Command status to 'Done'
    if post_args != None: 
        p_id = utils.get_arg(post_args,'ID')
        p_ret_code = utils.get_arg(post_args,'Return')
        p_cmd = utils.get_arg(post_args,'CMD')

        #TODO set ZK Command Status to 'Done'
        erpnext_status_code, erpnext_message = update_command_status(p_id, "Done")
        try:
            if erpnext_status_code == 200:
                ret_msg = "OK"
            elif erpnext_status_code == 404:
                ret_msg = "ERR:Command '" + p_id + "' does not exist!"
            else:
                ret_msg = "Err:" + str(erpnext_status_code) + ":" + erpnext_message
        except frappe.DoesNotExistError:
            ret_msg = "ERR:Command '" + p_id + "' does not exist!"
        except Exception as e:
            logger.exception('ERR:' + str(e))
            ret_msg = "ERROR"

        erpnext_status_code, erpnext_message = update_terminal_last_activity(serial_number)
        try:
            if erpnext_status_code == 200:
                ret_msg = "OK"
            elif erpnext_status_code == 404:
                ret_msg = "ERR:Command '" + serial_number + "' does not exist!"
            else:
                ret_msg = "Err:" + str(erpnext_status_code) + ":" + erpnext_message
        except frappe.DoesNotExistError:
            ret_msg = "ERR:Command '" + serial_number + "' does not exist!"
        except Exception as e:
            logger.exception('ERR:' + str(e))
            ret_msg = "ERROR"

    if ret_msg == "OK":
        # update ZK Terminal with info
        try:
            erpnext_status_code, erpnext_message = save_terminal(serial_number, info)
            if erpnext_status_code == 200:
                ret_msg = "OK"
            elif erpnext_status_code == 404:
                ret_msg = "ERR:Terminal '" + serial_number + "' does not exist!"
            else:
                ret_msg = "Err:" + str(erpnext_status_code) + ":" + erpnext_message
        except frappe.DoesNotExistError:
            ret_msg = "ERR:Terminal '" + serial_number + "' does not exist!"
        except Exception as e:
            logger.exception('ERR:' + str(e))
            ret_msg = "ERROR"

    return ret_msg

def save_terminal(serial_number, info):
    """
    Example: save_terminal('CCK24212349', info)
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK Terminal/" + serial_number
    headers = utils.get_headers()

    data = {
        'fw_version' : info.get('FWVersion',info.get('FirmVer',"")),
        'ip_address' : info['IPAddress'],
        'model' : info['~DeviceName'],
        'platform' : info.get('~Platform',""),
        'push_version' : info['PushVersion']
	}

    response = requests.request("PUT", url, headers=headers, json=data)
    if response.status_code == 200:
        print("response.content",response._content)
        return 200, json.loads(response._content)['data']['name']
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(serial_number), str(info),  error_str]))
        return response.status_code, error_str


def create_attendance(employee_field_value, timestamp, device_id=None, log_type=None):
    """
    Example: create_attendance('12349',datetime.datetime.now(),'HO1','IN')
    """
    url = f"{config.ERPNEXT_URL}/api/method/hrms.hr.doctype.employee_checkin.employee_checkin.add_log_based_on_employee_field"
    headers = utils.get_headers()

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
        error_str = utils.safe_get_error_str(response)
        if EMPLOYEE_NOT_FOUND_ERROR_MESSAGE in error_str:
            print('\t'.join(['Error during ERPNext API Call.', str(employee_field_value), str(timestamp.timestamp()), str(device_id), str(log_type), error_str]))
        else:
            print('\t'.join(['Error during ERPNext API Call.', str(employee_field_value), str(timestamp.timestamp()), str(device_id), str(log_type), error_str]))
        return response.status_code, error_str



def get_terminal_alias(serial_number):
    """
    Example: get_terminal_alias('CBE13422349')
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK Terminal/" + serial_number
    headers = utils.get_headers()
    data = {
    }
    response = requests.request("GET", url, headers=headers, json=data)
    if response.status_code == 200:
        return 200, json.loads(response._content)['data']['alias']
    else:
        error_str = utils.safe_get_error_str(response)
        if EMPLOYEE_NOT_FOUND_ERROR_MESSAGE in error_str:
            print('\t'.join(['Error during ERPNext API Call.', str(serial_number), error_str]))
        else:
            print('\t'.join(['Error during ERPNext API Call.', str(serial_number), error_str]))
        return response.status_code, error_str



def setup_logger(name, log_file, level=logging.INFO, formatter=None):
	if not formatter:
		formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')

	handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=50)
	handler.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(level)
	if not logger.hasHandlers():
		logger.addHandler(handler)

	return logger


def update_terminal_last_activity(serial_number):
    """
    Example: update_terminal_last_activity('CCK24212349')
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK Terminal/" + serial_number
    headers = utils.get_headers()

    now = datetime.datetime.now()

    data = {
        'last_activity' : now.__str__()
	}

    response = requests.request("PUT", url, headers=headers, json=data)
    if response.status_code == 200:
        print("response.content",response._content)
        return 200, json.loads(response._content)['data']['name']
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(serial_number), now.__str__,  error_str]))
        return response.status_code, error_str