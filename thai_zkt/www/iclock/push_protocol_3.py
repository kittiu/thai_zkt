from urllib.parse import parse_qs, urlparse
import thai_zkt.www.iclock.local_config as config
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.service as service
import frappe
from asyncio.log import logger

CMD_GET_INFO = "_GET_OPTIONS"
CMD_CLEAR_USERS = "DATA DELETE user Pin=*"
CMD_GET_USERS = "_CHECK"
CMD_SET_USERS = "_UPDATE"

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
    , "ServerVer=3.1.2"
    , "PushProtVer=3.1.2"
    , "Encrypt=0"
    , "SupportPing=1"
    , "PushOptionsFlag=1"
    , "MaxPostSize=1048576"
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


def handle_push_post(serial_number):
    
    print("handle_push_post()")
    
    ret_msg = "\n".join([f"ServerVer=3.1.2"
    , "ServerName=Thai ZKT"
    , "PushVersion=3.1.2"
    , "ErrorDelay=60"
    , "RequestDelay=2"
    , "TransInterval=2"
    , "TransTables=User Transaction"
    , "Realtime=1"
    , "SessionID=1111"
    , "TimeoutSec=10"
    , "BioPhotoFun=1"
    , "BioDataFun=1"
    , "MultiBioDataSupport=0:1:1:0:0:0:0:1:1:1"
    , "MultiBioPhotoSupport=0:0:0:0:0:0:0:0:0:1\n"])
    
    return ret_msg


def cmd_get_options(serial_number):
    print("cmd_get_options()")

    cmd_line_1 = "GET OPTIONS " + get_options_1()
    status, new_cmd_id_1 = service.create_command(serial_number, cmd_line_1, 'Sent')

    cmd_line_2 = "GET OPTIONS " + get_options_2()
    status, new_cmd_id_2 = service.create_command(serial_number, cmd_line_2, 'Sent')

    cmd_line_3 = "GET OPTIONS " + get_options_3()
    status, new_cmd_id_3 = service.create_command(serial_number, cmd_line_3, 'Sent')

    cmd_line_4 = "GET OPTIONS " + get_options_4()
    status, new_cmd_id_4 = service.create_command(serial_number, cmd_line_4, 'Sent')

    ret_msg = "\d\n\d\n".join(["C:"+ new_cmd_id_1 +":" + cmd_line_1
                             , "C:"+ new_cmd_id_2 +":" + cmd_line_2
                             , "C:"+ new_cmd_id_3 +":" + cmd_line_3
                             , "C:"+ new_cmd_id_4 +":" + cmd_line_4
                             ]) + "\d\n\d\n"

    return ret_msg


def get_options_1():
    ret_msg = "~SerialNumber,FirmVer,~DeviceName,LockCount,ReaderCount,AuxInCount,AuxOutCount,MachineType,~IsOnlyRFMachine,~MaxUserCount,~MaxAttLogCount,~MaxFingerCount,~MaxUserFingerCount,MThreshold,NetMask,GATEIPAddress,~ZKFPVersion,SimpleEventType,VerifyStyles,EventTypes,ComPwd,MaxMCUCardBits,NewVFStyles,IPAddress,CommType"
    return ret_msg
    
def get_options_2():
    ret_msg = "~SerialNumber,IclockSvrFun,OverallAntiFunOn,~REXInputFunOn,~CardFormatFunOn,~SupAuthrizeFunOn,~ReaderCFGFunOn,~ReaderLinkageFunOn,~RelayStateFunOn,~Ext485ReaderFunOn,~TimeAPBFunOn,~CtlAllRelayFunOn,~LossCardFunOn,DisableUserFunOn,DeleteAndFunOn,LogIDFunOn,DateFmtFunOn,DelAllLossCardFunOn,DelayOpenDoorFunOn,UserOpenDoorDelayFunOn,MultiCardInterTimeFunOn,DSTFunOn,OutRelaySetFunOn,MachineTZFunOn,AutoServerFunOn,PC485AsInbio485,MasterInbio485,RS232BaudRate,AutoServerMode,IPCLinkFunOn"
    return ret_msg
    
def get_options_3():
    ret_msg = "~SerialNumber,IPCLinkServerIP,MasterControlOn,SubControlOn,AccSupportFunList,MaskDetectionFunOn,IRTempDetectionFunOn"
    return ret_msg

def get_options_4():
    ret_msg = "~SerialNumber,FingerFunOn,FvFunOn,FaceFunOn,~MaxFace7Count,~MaxFvCount,EnalbeIRTempDetection,EnableNormalIRTempPass,EnalbeMaskDetection,EnableWearMaskPass,IRTempThreshold,IRTempUnit,EnableUnregisterPass,EnableTriggerAlarm,IRTempCorrection"
    return ret_msg

def cmd_check(serial_number):
    print("cmd_check()")

    cmd_line_1 = "DATA QUERY tablename=user,fielddesc=*,filter=*"
    status, new_cmd_id_1 = service.create_command(serial_number, cmd_line_1, 'Sent')

    cmd_line_2 = "DATA QUERY tablename=biodata,fielddesc=*,filter=Type=1"
    status, new_cmd_id_2 = service.create_command(serial_number, cmd_line_2, 'Sent')

    cmd_line_3 = "DATA QUERY tablename=biodata,fielddesc=*,filter=Type=9"
    status, new_cmd_id_3 = service.create_command(serial_number, cmd_line_3, 'Sent')

    cmd_line_4 = "DATA QUERY tablename=biophoto,fielddesc=*,filter=*"
    status, new_cmd_id_4 = service.create_command(serial_number, cmd_line_4, 'Sent')

    ret_msg = "\d\n\d\n".join(["C:"+ new_cmd_id_1 +":" + cmd_line_1
                             , "C:"+ new_cmd_id_2 +":" + cmd_line_2
                             , "C:"+ new_cmd_id_3 +":" + cmd_line_3
                             , "C:"+ new_cmd_id_4 +":" + cmd_line_4
                             ]) + "\d\n\d\n"

    return ret_msg


def handle_querydata_post_options(serial_number,data):
    ret_msg = "OK"
    
    #TODO loop data
        # if exists
            # update
        # else
            # add
            
    ret_msg = service.set_terminal_options(serial_number,data)
    
    return ret_msg


def handle_querydata_post_tabledata_user(data):
    ret_msg = "OK"
    
    lines = data.split("\n")
    print("lines:",lines)

    user_cnt = 0

    for line in lines:
        words = line.split("\t")
        print("words:",words)

        if words[0].startswith("user uid"):
            kv = words[0].split("=")
            user_id = kv[1]
            kv = words[2].split("=")
            pin = kv[1]
            kv = words[7].split("=")
            user_name = kv[1]
            kv = words[8].split("=")
            user_pri = kv[1]
            kv = words[3].split("=")
            user_password = kv[1]
            kv = words[4].split("=")
            user_grp = kv[1]

            erpnext_status_code, erpnext_message = service.create_user(pin, user_name, user_pri, user_password, user_grp, user_id)
            print("erpnext_status_code:",erpnext_status_code)
            if erpnext_status_code == 200:
                user_cnt += 1

    if user_cnt > 0:
        ret_msg = "user=" + str(user_cnt)
    
    return ret_msg


def handle_querydata_post_tabledata_biodata(data):
    ret_msg = "OK"
    
    lines = data.split("\r\n")
    print("lines:",lines)

    biodata_cnt = 0

    for line in lines:
        words = line.split("\t")
        print("words:",words)

        if words[0].startswith("biodata"):
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
            #kv = words[9].split("=")
            template = words[9][4:]

            erpnext_status_code, erpnext_message = service.create_bio_data(zk_user, type, no, index, valid, format, major_version, minor_version, template)
            print("erpnext_status_code:",erpnext_status_code)
            if erpnext_status_code == 200:
                biodata_cnt += 1

    if biodata_cnt > 0:
        ret_msg = "biodata=" + str(biodata_cnt)
    
    return ret_msg


def handle_querydata_post_tabledata_biophoto(data):
    ret_msg = "OK"
    
    lines = data.split("\n")
    print("lines:",lines)

    biodata_cnt = 0

    for line in lines:
        words = line.split("\t")
        print("words:",words)

        if words[0].startswith("biophoto"):
            kv = words[0].split("=")
            zk_user = kv[1]
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

            erpnext_status_code, erpnext_message = service.create_bio_photo(zk_user, type, no, index, file_name, size, content)
            print("erpnext_status_code:",erpnext_status_code)
            if erpnext_status_code == 200:
                biodata_cnt += 1

    if biodata_cnt > 0:
        ret_msg = "biophoto=" + str(biodata_cnt)
    
    return ret_msg


def get_cmd_update_user(user):
    return 'DATA UPDATE user ' + encode_user(user)

def get_cmd_update_biodata(data):
    return 'DATA UPDATE biodata ' + encode_biodata(data)

def get_cmd_update_biophoto(data):
    return 'DATA UPDATE biophoto ' + encode_biophoto(data)

def encode_user(user):
    
    encode = "\t".join(["Cardno="
                           ,"Pin=" + str(user["id"])
                           ,"Password=" + user["password"]
                           ,"Group=" + user["group"]
                           ,"Starttime=0"
                           ,"Endtime=0"
                           ,"Name=" + user["user_name"]
                           ,"Privilege=" + user["privilege"]
                           ,"Disable=0"
                           ,"Verify=0"
                           ])
    return encode

def encode_biodata(biodata):
    
    #format = "ZK" if biodata["format"]==0 else str(biodata["format"])
    format = str(biodata["format"])

    encode = "\t".join(["Pin=" + str(biodata["zk_user"])
                           ,"No=" + str(biodata["no"])
                           ,"Index="+ str(biodata["index"])
                           ,"Valid="+ str(biodata["valid"])
                           ,"Duress=0"
                           ,"Type="+ str(biodata["type"])
                           ,"Majorver=" + biodata["major_version"]
                           ,"Minorver=" + biodata["minor_version"]
                           ,"Format=" + format
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

            for user in users:
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