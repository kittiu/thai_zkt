from urllib.parse import parse_qs, urlparse
import thai_zkt.www.iclock.local_config as config
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.service as service
import frappe
from asyncio.log import logger

CMD_GET_INFO = "INFO"
CMD_CLEAR_USERS = "DATA DELETE USERINFO"
CMD_GET_USERS = "CHECK"

def handle_cdata_get(args):
    
    print("handle_cdata_get()")
    
    serial_number = utils.get_arg(args,'SN')
    print("Serial Number:",serial_number)

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
    
    ret_msg = "\n".join([f"GET OPTION FROM: {serial_number}"
    , "TransFlag=TransData AttLog	OpLog	AttPhoto	EnrollFP	EnrollUser	FPImag	ChgUser	ChgFP	FACE	UserPic	FVEIN	BioPhoto"
    , "ServerVer=2.4.1"
    , "PushProtVer=2.4.1"
    , "Encrypt=0"
    , "EncryptFlag=1000000000"
    , "SupportPing=1"
    , "PushOptionsFlag=1"
    , "MaxPostSize=1048576"
    , "PushOptions=UserCount,TransactionCount,FingerFunOn,FPVersion,FPCount,FaceFunOn,FaceVersion,FaceCount,FvFunOn,FvVersion,FvCount,PvFunOn,PvVersion,PvCount,BioPhotoFun,BioDataFun,PhotoFunOn,~LockFunOn,CardProtFormat,~Platform,MultiBioPhotoSupport,MultiBioDataSupport,MultiBioVersion"
    , "MultiBioDataSupport=0:1:1:0:0:0:0:1:1:1:1"
    , "MultiBioPhotoSupport=0:0:0:0:0:0:0:0:0:1:0"
    , "TimeZone=7"
    , "TransTimes=00:00;14:05"
    , "TransInterval=1"
    , "ErrorDelay=60"
    , "Delay=10"
    , "Realtime=1"
    , "Stamp=1716809648.0"
    , "OpStamp=0"
    , "PhotoStamp=0\n"])
    
    return ret_msg


def get_cmd_update_user(user):
    return 'DATA UPDATE USERINFO ' + encode_user(user)

def get_cmd_update_biodata(data):
    return 'DATA UPDATE BIODATA ' + encode_biodata(data)

def get_cmd_update_biophoto(data):
    return 'DATA UPDATE BIOPHOTO ' + encode_biophoto(data)

def get_cmd_delete_user(user):
    return 'DATA DELETE USERINFO PIN=' + user

def encode_user(user):
    
    encode = "\t".join(["PIN=" + str(user["id"])
                           ,"Name=" + user["user_name"]
                           ,"Pri=" + user["privilege"]
                           ,"Passwd=" + user["password"]
                           ,"Card="
                           ,""
                           ,"Grp=" + user["group"]
                           ,"Verify=0"
                           ])
    
    return encode

def encode_biodata(biodata):
	
	encode = "\t".join(["Pin=" + str(biodata["zk_user"])
                           ,"No=" + str(biodata["no"])
                           ,"Index="+ str(biodata["index"])
                           ,"Valid="+ str(biodata["valid"])
                           ,"Duress=0"
                           ,"Type="+ str(biodata["type"])
                           ,"MajorVer=" + biodata["major_version"]
                           ,"MinorVer=" + biodata["minor_version"]
                           ,"Tmp="+biodata["template"]
                           ])

	return encode

def encode_biophoto(biophoto):
    encode = "\t".join(["PIN=" + str(biophoto["zk_user"])
                           ,"Type="+ str(biophoto["type"])
                           ,"Size=" + str(biophoto["size"])
                           ,"Format=0"
                           ,"PostBackTmpFlag=0"
                           ,"Url=1.jpg"
                           ,"Content="+biophoto["content"]
                           ])

    return encode


def gen_download_user_cmds(serial_number):
    
    # loop ZK User
    #   create new command 'UPDATE USERINFO'
    #   if exists ZK Bio Data
    #     create new command 'UPDATE BIODATA'
    
    ret_msg = "OK"

    try:
        erpnext_status_code, erpnext_message = service.list_user()
        if erpnext_status_code == 200:
    
            users = erpnext_message
            
            print("users.len:",len(users))

            for user in users:
                create_update_user_command(user, serial_number)
    
        elif erpnext_status_code == 404:
            ret_msg = "ERR:ZK User does not exist!"
        else:
            ret_msg = "ERR:" + str(erpnext_status_code) + ":" + erpnext_message
    except frappe.DoesNotExistError:
        ret_msg = "ERR:ZK User does not exist!"
    except Exception as e:
        logger.exception('ERR:' + str(e))
        ret_msg = "ERROR"

    return ret_msg


def create_update_user_command(user, serial_number, add_after_done=False):
    
    after_done = ""
    if add_after_done:
        after_done = '{"action":"update_sync_terminal","pin":'+str(user.get("id"))+'}'
    
    cmd_line = get_cmd_update_user(user)
    status, new_cmd_id = service.create_command(serial_number, cmd_line, 'Create', after_done)
    
    #create UPDATE BIODATA command
    try:
        erpnext_status_code, erpnext_message = service.list_biodata(user["id"])
        if erpnext_status_code == 200:

            biodata = erpnext_message

            for data in biodata:
                cmd_line = get_cmd_update_biodata(data)
                status, new_cmd_id = service.create_command(serial_number, cmd_line, 'Create')

        elif erpnext_status_code == 404:
            ret_msg = "ERR:ZK Bio Data of User '" + user["id"] + "' does not exist!"
        else:
            ret_msg = "ERR:" + str(erpnext_status_code) + ":" + erpnext_message
    except frappe.DoesNotExistError:
        ret_msg = "ERR:ZK Bio Data of User '" + user["id"] + "' does not exist!"
    except Exception as e:
        logger.exception('ERR:' + str(e))
        ret_msg = "ERROR"

    #create UPDATE BIOPHOTO command
    try:
        erpnext_status_code, erpnext_message = service.list_biophoto(user["id"])
        if erpnext_status_code == 200:

            biophoto = erpnext_message

            for data in biophoto:
                cmd_line = get_cmd_update_biophoto(data)
                status, new_cmd_id = service.create_command(serial_number, cmd_line, 'Create')
                
        elif erpnext_status_code == 404:
            ret_msg = "ERR:ZK Bio Photo of User '" + user["id"] + "' does not exist!"
        else:
            ret_msg = "ERR:" + str(erpnext_status_code) + ":" + erpnext_message
    except frappe.DoesNotExistError:
        ret_msg = "ERR:ZK Bio Photo of User '" + user["id"] + "' does not exist!"
    except Exception as e:
        logger.exception('ERR:' + str(e))
        ret_msg = "ERROR"



def create_delete_user_command(user, serial_number, add_after_done=False):
    
    after_done = ""
    if add_after_done:
        after_done = '{"action":"update_sync_terminal","pin":'+str(user.get("id"))+'}'

    cmd_line = get_cmd_delete_user(str(user.get("id")))
    status, new_cmd_id = service.create_command(serial_number, cmd_line, 'Create', after_done)


def handle_cdata_post_attlog(serial_number, data):
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

    service.save_attendance(serial_number, logs)


def handle_cdata_post_biodata(is_main, data):
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

            if is_main:
                erpnext_status_code, erpnext_message = service.save_bio_data(zk_user, type, no, index, valid, format, major_version, minor_version, template)
            
            template_cnt += 1

    if template_cnt > 0:
        ret_msg = "OK:" + str(template_cnt) + "\n"
    else:
        ret_msg = "OK"

    return ret_msg


def handle_cdata_post_operlog(is_main, data):
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

            if is_main:
                erpnext_status_code, erpnext_message = service.save_user(pin, user_name, user_pri, user_password, user_grp)

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

            if is_main:
                erpnext_status_code, erpnext_message = service.save_bio_photo(pin, type, no, index, file_name, size, content)

            item_cnt += 1
            
    if item_cnt > 0:
        ret_msg = "OK:" + str(item_cnt) + "\n"
    else:
        ret_msg = "OK"

    return ret_msg


def handle_querydata_post_options(serial_number,data):
    ret_msg = "OK"
    
    ret_msg = service.set_terminal_options(serial_number, data)
    
    return ret_msg