
# # ERPNext related configs
# ERPNEXT_API_KEY = 'd4033010702172e'
# ERPNEXT_API_SECRET = 'f565902002bf6ee'
# ERPNEXT_URL = 'http://dcode.com:8000'

# # operational configs
# LOGS_DIRECTORY = '/home/cooper/logs' # logs of this script is stored in this directory

ERPNEXT_API_KEY = 'e5b449d6e84fb6c'
ERPNEXT_API_SECRET = 'd316585a947c5d5'
ERPNEXT_URL = 'http://192.168.147.227:8000/'

# operational configs
LOGS_DIRECTORY = '/tmp' # logs of this script is stored in this directory

# Ignore following exceptions thrown by ERPNext and continue importing punch logs.
# Note: All other exceptions will halt the punch log import to erpnext.
#       1. No Employee found for the given employee User ID in the Biometric device.
#       2. Employee is inactive for the given employee User ID in the Biometric device.
#       3. Duplicate Employee Checkin found. (This exception can happen if you have cleared the logs/status.json of this script)
# Use the corresponding number to ignore the above exceptions. (Default: Ignores all the listed exceptions)
allowed_exceptions = [1,2,3]

# Q:kittiu
# - what is logs/status.json?
