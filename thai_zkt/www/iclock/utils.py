import datetime
import json
import thai_zkt.www.iclock.local_config as config

def get_arg(args,key,index=0,default=""):
    return args.get(key)[index] if args.get(key) else default

def safe_convert_date(datestring, pattern):
    try:
        print("_safe_convert_date("+datestring+" , "+pattern+")")
        return datetime.datetime.strptime(datestring, pattern)
    except:
        print("_safe_convert_date(None)")
        return None

def safe_get_error_str(res):
    try:
        error_json = json.loads(res._content)
        if 'exc' in error_json: # this means traceback is available
            error_str = json.loads(error_json['exc'])[0]
        else:
            error_str = json.dumps(error_json)
    except:
        error_str = str(res.__dict__)
    return error_str

def get_headers():
    
    return {
        'Authorization': "token "+ config.ERPNEXT_API_KEY + ":" + config.ERPNEXT_API_SECRET,
        'Accept': 'application/json'
    }
