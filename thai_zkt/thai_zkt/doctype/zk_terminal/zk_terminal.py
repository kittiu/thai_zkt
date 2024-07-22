# Copyright (c) 2024, Ecosoft Co., Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ZKTerminal(Document):
	pass


@frappe.whitelist()
def clear_terminal_user(terminal):
    
    cmd = frappe.get_doc({"doctype":"ZK Command", "terminal":terminal, "command":"DATA DELETE user Pin=*"})
    cmd.insert()
    
    return "OK"


@frappe.whitelist()
def download_terminal_user(terminal):
    
    cmd = frappe.get_doc({"doctype":"ZK Command", "terminal":terminal, "command":"_UPDATE"})
    cmd.insert()
    
    return "OK"