# Copyright (c) 2024, Ecosoft Co., Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import thai_zkt.www.iclock.service as service

class ZKTerminal(Document):
	pass

@frappe.whitelist()
def get_terminal_info(terminal):
    
    push = service.get_push_protocol(terminal)
    
    cmd = frappe.get_doc({"doctype":"ZK Command", "terminal":terminal, "command":push.CMD_GET_INFO})
    cmd.insert()

    return "OK"


@frappe.whitelist()
def clear_terminal_user(terminal):
    
    push = service.get_push_protocol(terminal)
    
    cmd = frappe.get_doc({"doctype":"ZK Command", "terminal":terminal, "command":push.CMD_CLEAR_USERS})
    cmd.insert()
    
    return "OK"


@frappe.whitelist()
def download_terminal_user(terminal):
    
    push = service.get_push_protocol(terminal)
    
    cmd = frappe.get_doc({"doctype":"ZK Command", "terminal":terminal, "command":push.CMD_SET_USERS})
    cmd.insert()
    
    return "OK"


@frappe.whitelist()
def upload_terminal_user(terminal):
    
    push = service.get_push_protocol(terminal)
    
    cmd = frappe.get_doc({"doctype":"ZK Command", "terminal":terminal, "command":push.CMD_GET_USERS})
    cmd.insert()
    
    return "OK"
