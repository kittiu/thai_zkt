import frappe
from asyncio.log import logger
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.local_config as config
import requests
import json
import logging
import datetime
from logging.handlers import RotatingFileHandler
import thai_zkt.www.iclock.push_protocol_2 as push2
import thai_zkt.www.iclock.push_protocol_3 as push3


EMPLOYEE_NOT_FOUND_ERROR_MESSAGE = "No Employee found for the given employee field value"
EMPLOYEE_INACTIVE_ERROR_MESSAGE = "Transactions cannot be created for an Inactive Employee"
DUPLICATE_EMPLOYEE_CHECKIN_ERROR_MESSAGE = "This employee already has a log with the same timestamp"
allowlisted_errors = [EMPLOYEE_NOT_FOUND_ERROR_MESSAGE, EMPLOYEE_INACTIVE_ERROR_MESSAGE, DUPLICATE_EMPLOYEE_CHECKIN_ERROR_MESSAGE]

if hasattr(config,'allowed_exceptions'):
    allowlisted_errors_temp = []
    for error_number in config.allowed_exceptions:
        allowlisted_errors_temp.append(allowlisted_errors[error_number-1])
    allowlisted_errors = allowlisted_errors_temp

def update_command_list_status(cmd_id_list, status):
    """
    Example: update_command_list_status([1,2,3], "Sent")
    """
    
    url = f"{config.ERPNEXT_URL}/api/method/thai_zkt.api.update_command_list_status"
    headers = utils.get_headers()
    data = {
        "cmd_id_list":cmd_id_list,
        "status":status
    }

    print("data:",data)

    response = requests.request("POST", url, headers=headers, json=data)
    if response.status_code == 200:
        #print("response.content",response._content)
        return 200, "OK"
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during API Call.', str(cmd_id_list), str(status),  error_str]))
        return response.status_code, error_str


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
        #print("response.content",response._content)
        return 200, json.loads(response._content)['data']['name']
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(cmd_id), str(status),  error_str]))
        return response.status_code, error_str

def update_terminal_info(serial_number, info):

    ret_msg = "OK"

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
            print("info.pushver:",info.get("PushVersion",""))
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

    data = {}

    fw_version = info.get('FWVersion',info.get('FirmVer',""))
    if fw_version:
        data['fw_version'] = fw_version
    
    if info.get('~Platform') != None:
        data['platform'] = info['~Platform']
        
    if info.get('IPAddress') != None:
        data['ip_address'] = info['IPAddress']
        
    if info.get('~DeviceName') != None:
        data['model'] = info['~DeviceName']

    if info.get('PushVersion') != None:
        data['push_version'] = info['PushVersion']
        
    if info.get('DeviceType') != None:
        data['device_type'] = info['DeviceType']

    print("save_terminal() data:",data)

    response = requests.request("PUT", url, headers=headers, json=data)
    if response.status_code == 200:
        #print("response.content",response._content)
        return 200, json.loads(response._content)['data']['name']
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(serial_number), str(info),  error_str]))
        return response.status_code, error_str

def update_terminal_option(serial_number, options):

    ret_msg = "OK"

    # delete old ZK Terminal options
    try:
        erpnext_status_code, erpnext_message = delete_terminal_option(serial_number)
        if erpnext_status_code == 200:
            ret_msg = "OK"
        else:
            ret_msg = "Err:" + str(erpnext_status_code) + ":" + erpnext_message
    except Exception as e:
        logger.exception('ERR:' + str(e))
        ret_msg = "ERROR"


    if ret_msg == "OK":
        # update ZK Terminal with options
        for key,value in options.items():
            try:
                erpnext_status_code, erpnext_message = create_terminal_option(serial_number, key, value)
                if erpnext_status_code == 200:
                    ret_msg = "OK"
                else:
                    ret_msg = "Err:" + str(erpnext_status_code) + ":" + erpnext_message
            except frappe.DoesNotExistError:
                ret_msg = "ERR:ZK Terminal Option'" + serial_number + "' does not exist!"
            except Exception as e:
                logger.exception('ERR:' + str(e))
                ret_msg = "ERROR"
            if ret_msg != "OK":
                break

    return ret_msg

def delete_terminal_option(serial_number):
    """
    Example: delete_terminal_option('CCK24212349')
    """
    url = f"{config.ERPNEXT_URL}/api/method/thai_zkt.api.delete_terminal_option"
    
    headers = utils.get_headers()

    data = {
        "zk_terminal":serial_number
    }

    response = requests.request("POST", url, headers=headers, json=data)
    if response.status_code == 200:
        #print("response.content",response._content)
        return 200, response._content
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(serial_number), error_str]))
        return response.status_code, error_str


def create_terminal_option(serial_number, key, value):
    """
    Example: create_terminal_option('CCK24212349', "ProtVer", "3.1.2")
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK Terminal Option"
    headers = utils.get_headers()

    data = {
        "zk_terminal":serial_number,
        "key":key,
        "value":value
    }

    response = requests.request("POST", url, headers=headers, json=data)
    if response.status_code == 200:
        return 200, json.loads(response._content)['data']['name']
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(serial_number), str(key), str(value),  error_str]))
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


def get_terminal(serial_number):
    """
    Example: get_terminal('CBE13422349')
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK Terminal/" + serial_number
    headers = utils.get_headers()
    data = {
    }
    response = requests.request("GET", url, headers=headers, json=data)
    if response.status_code == 200:
        return 200, json.loads(response._content)['data']
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
        #print("response.content",response._content)
        return 200, json.loads(response._content)['data']['name']
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(serial_number), now.__str__,  error_str]))
        return response.status_code, error_str
    
def create_user(user_id, user_name, user_pri, user_password, user_grp, pin):
    """
    Example: create_user('1','Roger Power', '1', 'abc', '1')
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK User"
    headers = utils.get_headers()

    data = {
        'id' : user_id,
        'user_name' : user_name,
        'password' : user_password,
        'privilege' : user_pri,
        'group' : user_grp,
        'pin' : pin
	}
    
    response = requests.request("POST", url, headers=headers, json=data)
    if response.status_code == 200:
        #print("response.content",response._content)
        return 200, json.loads(response._content)['data']['id']
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(id), str(user_name),  error_str]))
        return response.status_code, error_str
    
    
def create_bio_data(zk_user, type, no, index, valid, format, major_version, minor_version, template):
    """
    Example: create_bio_data('CCK24212349', info)
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK Bio Data"
    headers = utils.get_headers()

    data = {
        'zk_user' : zk_user,
        'type' : type,
        'no' : no,
        'index' : index,
        'valid' : valid,
        'format' : format,
        'major_version' : major_version,
        'minor_version' : minor_version,
        'template' : template
	}
    
    response = requests.request("POST", url, headers=headers, json=data)
    if response.status_code == 200:
        #print("response.content",response._content)

        return 200, json.loads(response._content)['data']['name']
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(zk_user), str(type), str(no), str(index),  error_str]))
        return response.status_code, error_str


def create_bio_photo(zk_user, type, no, index, file_name, size, content):
    """
    Example: create_bio_photo('CCK24212349', info)
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK Bio Photo"
    headers = utils.get_headers()

    data = {
        'zk_user' : zk_user,
        'type' : type,
        'no' : no,
        'index' : index,
        'file_name' : file_name,
        'size' : size,
        'content' : content
	}
    
    response = requests.request("POST", url, headers=headers, json=data)
    if response.status_code == 200:
        #print("response.content",response._content)

        return 200, json.loads(response._content)['data']['name']
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(zk_user), str(type), str(no), str(index),  error_str]))
        return response.status_code, error_str    
    
    
def list_user(search_term = None):
    """
    Example: list_user('CBE13422349')
    """
    fields = 'fields=["id","user_name","password","privilege","group","uid"]'
    url = f'{config.ERPNEXT_URL}/api/resource/ZK User?{fields}&limit_start=0&limit=500'
    headers = utils.get_headers()
    
    #if search_term:
    #    data['user_name'] = search_term
    
    response = requests.request("GET", url=url, headers=headers)
    print("response.status_code:{}".format(response.status_code))
    if response.status_code == 200:
        return 200, json.loads(response._content)['data']
    else:
        error_str = utils.safe_get_error_str(response)
        if EMPLOYEE_NOT_FOUND_ERROR_MESSAGE in error_str:
            print('\t'.join(['Error during ERPNext API Call.', str(search_term), error_str]))
        else:
            print('\t'.join(['Error during ERPNext API Call.', str(search_term), error_str]))
        return response.status_code, error_str

def list_biodata(user_id):
    """
    Example: list_biodata(1)
    """
    fields = 'fields=["zk_user","type","no","index","valid","valid","format","major_version","minor_version","template"]'
    filters = f'filters=[["zk_user","=",{user_id}]]'
    url = f'{config.ERPNEXT_URL}/api/resource/ZK Bio Data?{fields}&{filters}'
    headers = utils.get_headers()
    
    response = requests.request("GET", url=url, headers=headers)
    print("response.status_code:{}".format(response.status_code))
    if response.status_code == 200:
        print("==================================")
        print("response._content:",response._content)
        print("==================================")
        return 200, json.loads(response._content)['data']
    else:
        error_str = utils.safe_get_error_str(response)
        if EMPLOYEE_NOT_FOUND_ERROR_MESSAGE in error_str:
            print('\t'.join(['Error during ERPNext API Call.', str(user_id), error_str]))
        else:
            print('\t'.join(['Error during ERPNext API Call.', str(user_id), error_str]))
        return response.status_code, error_str
    

def list_biophoto(user_id):
    """
    Example: list_biophoto(1)
    """
    fields = 'fields=["zk_user","type","no","index","file_name","size","content"]'
    filters = f'filters=[["zk_user","=",{user_id}]]'
    url = f'{config.ERPNEXT_URL}/api/resource/ZK Bio Photo?{fields}&{filters}'
    headers = utils.get_headers()
    
    response = requests.request("GET", url=url, headers=headers)
    print("response.status_code:{}".format(response.status_code))
    if response.status_code == 200:
        print("==================================")
        print("response._content:",response._content)
        print("==================================")
        return 200, json.loads(response._content)['data']
    else:
        error_str = utils.safe_get_error_str(response)
        if EMPLOYEE_NOT_FOUND_ERROR_MESSAGE in error_str:
            print('\t'.join(['Error during ERPNext API Call.', str(user_id), error_str]))
        else:
            print('\t'.join(['Error during ERPNext API Call.', str(user_id), error_str]))
        return response.status_code, error_str
        
    
def get_user(name):
    """
    Example: list_user('CBE13422349')
    """
    url = f'{config.ERPNEXT_URL}/api/resource/ZK User/{name}'
    headers = utils.get_headers()
    data = {}
    
    response = requests.request("GET", url, headers=headers, json=data)
    if response.status_code == 200:
        return 200, json.loads(response._content)['data']
    else:
        error_str = utils.safe_get_error_str(response)
        if EMPLOYEE_NOT_FOUND_ERROR_MESSAGE in error_str:
            print('\t'.join(['Error during ERPNext API Call.', str(name), error_str]))
        else:
            print('\t'.join(['Error during ERPNext API Call.', str(name), error_str]))
        return response.status_code, error_str



def create_command(terminal, command, status):
    """
    Example: create_command(1,'CSE33412349', 'UPDATE USERINFO', 'Sent')
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK Command"
    headers = utils.get_headers()

    data = {
        'terminal' : terminal,
        'command' : command,
        'status' : status
	}
    
    response = requests.request("POST", url, headers=headers, json=data)
    if response.status_code == 200:
        return 200, str(json.loads(response._content)['data']['name'])
    else:
        error_str = utils.safe_get_error_str(response)
        if EMPLOYEE_NOT_FOUND_ERROR_MESSAGE in error_str:
            print('\t'.join(['Error during ERPNext API Call.', str(id), str(terminal), str(command), str(status), error_str]))
        else:
            print('\t'.join(['Error during ERPNext API Call.', str(id), str(terminal), str(command), str(status), error_str]))
        return response.status_code, error_str
    
def get_options_dict(data):
    lines = data.split(",")

    # resolve "~OEMVendor=ZKTECO CO., LTD." (Comma is inside company name)
    finallines = []
    idx = 0
    for line in lines:
        if len(line)>0:
            if "=" in line:
                finallines.append(line)
                idx += 1
            else:
                finallines[idx-1] = finallines[idx-1] + "," + line

    options = {}
    for ldx, line in enumerate(finallines):
        if len(line)>0:
            words = line.split("=")
            options[words[0]] = words[1]

    return options

    
def set_terminal_options(serial_number, options):

    ret_msg = "OK"

    old_options = ""
    
    # get ZK Terminal
    try:
        erpnext_status_code, erpnext_message = get_terminal(serial_number)
        if erpnext_status_code == 200:
            old_options = erpnext_message.get('options',"")
        else:
            ret_msg = "Err:" + str(erpnext_status_code) + ":" + erpnext_message
    except frappe.DoesNotExistError:
        ret_msg = "ERR:ZK Terminal Option'" + serial_number + "' does not exist!"
    except Exception as e:
        logger.exception('ERR:' + str(e))
        ret_msg = "ERROR"
        
    old_options_dict = get_options_dict(old_options)
    options_dict = get_options_dict(options)
    
    for key in options_dict:
        old_options_dict[key] = options_dict[key]
    
    options = ""
    for key in old_options_dict:
        options += key + "=" + old_options_dict[key] + ","

    if ret_msg == "OK":
        # set ZK Terminal options
        try:
            erpnext_status_code, erpnext_message = do_set_terminal_options(serial_number, options)
            if erpnext_status_code == 200:
                ret_msg = "OK"
            else:
                ret_msg = "Err:" + str(erpnext_status_code) + ":" + erpnext_message
        except frappe.DoesNotExistError:
            ret_msg = "ERR:ZK Terminal Option'" + serial_number + "' does not exist!"
        except Exception as e:
            logger.exception('ERR:' + str(e))
            ret_msg = "ERROR"

    return ret_msg


def get_terminal(serial_number):
    """
    Example: get_terminal('CBE13422349')
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK Terminal/" + serial_number
    headers = utils.get_headers()
    
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        return 200, json.loads(response._content)['data']
    else:
        error_str = utils.safe_get_error_str(response)
        if EMPLOYEE_NOT_FOUND_ERROR_MESSAGE in error_str:
            print('\t'.join(['Error during ERPNext API Call.', str(serial_number), error_str]))
        else:
            print('\t'.join(['Error during ERPNext API Call.', str(serial_number), error_str]))
        return response.status_code, error_str


def do_set_terminal_options(serial_number, options):
    """
    Example: do_set_terminal_options("CISK2239023", "~SerialNumber=CRJP234760207,FirmVer=ZMM510-NF24VB-Ver1.3.9,~DeviceName=SpeedFace-V3L/ID,LockCount=1,ReaderCount=2,AuxInCount=1,AuxOutCount=0,MachineType=101,~IsOnlyRFMachine=0,~MaxUserCount=30,~MaxAttLogCount=20")
    """
    url = f"{config.ERPNEXT_URL}/api/resource/ZK Terminal/{serial_number}"
    headers = utils.get_headers()

    data = {
        'options' : options
	}

    print("data:",data)

    response = requests.request("PUT", url, headers=headers, json=data)
    if response.status_code == 200:
        #print("response.content",response._content)
        return 200, json.loads(response._content)['data']['serial_number']
    else:
        error_str = utils.safe_get_error_str(response)
        print('\t'.join(['Error during ERPNext API Call.', str(serial_number), str(options),  error_str]))
        return response.status_code, error_str


def get_push_protocol(serial_number):
    
    code, terminal = get_terminal(serial_number)
    
    if terminal["push_version"].startswith("3"):
        print(serial_number,": Push Protocol V.3")
        push = push3
    else:
        print(serial_number,": Push Protocol V.2")
        push = push2
    
    return push