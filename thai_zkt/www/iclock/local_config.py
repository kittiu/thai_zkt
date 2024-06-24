
# ERPNext related configs
ERPNEXT_API_KEY = 'd4033010702172e'
ERPNEXT_API_SECRET = 'f565902002bf6ee'
ERPNEXT_URL = 'http://dcode.com:8000'
ERPNEXT_VERSION = 15


# operational configs
LOGS_DIRECTORY = '/home/cooper/logs' # logs of this script is stored in this directory

# Biometric device configs (all keys mandatory)
    #- device_id - must be unique, strictly alphanumerical chars only. no space allowed.
    #- ip - device IP Address
    #- punch_direction - 'IN'/'OUT'/'AUTO'/None
    #- clear_from_device_on_fetch: if set to true then attendance is deleted after fetch is successful.
                                    #(Caution: this feature can lead to data loss if used carelessly.)
devices = [
    {'device_id':'test_1','ip':'192.168.1.50', 'punch_direction': None, 'clear_from_device_on_fetch': False, 'serial_number':'CKII235260037'}
]

# Configs updating sync timestamp in the Shift Type DocType 
# please, read this thread to know why this is necessary https://discuss.erpnext.com/t/v-12-hr-auto-attendance-purpose-of-last-sync-of-checkin-in-shift-type/52997
shift_type_device_mapping = [
    {'shift_type_name': ['Shift1'], 'related_device_id': ['test_1']}
]


# Ignore following exceptions thrown by ERPNext and continue importing punch logs.
# Note: All other exceptions will halt the punch log import to erpnext.
#       1. No Employee found for the given employee User ID in the Biometric device.
#       2. Employee is inactive for the given employee User ID in the Biometric device.
#       3. Duplicate Employee Checkin found. (This exception can happen if you have cleared the logs/status.json of this script)
# Use the corresponding number to ignore the above exceptions. (Default: Ignores all the listed exceptions)
allowed_exceptions = [1,2,3]
