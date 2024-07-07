from urllib.parse import parse_qs, urlparse
import thai_zkt.www.iclock.local_config as config
import thai_zkt.www.iclock.utils as utils
import thai_zkt.www.iclock.service as service
import json


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