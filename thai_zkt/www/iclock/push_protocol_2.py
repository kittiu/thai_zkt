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


def create_update_user_command(user, serial_number):
    cmd_line = get_cmd_update_user(user)
    status, new_cmd_id = service.create_command(serial_number, cmd_line, 'Create')
    
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



def create_delete_user_command(user, serial_number):
    cmd_line = get_cmd_delete_user(str(user.get("id")))
    status, new_cmd_id = service.create_command(serial_number, cmd_line, 'Create')
