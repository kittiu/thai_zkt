# Copyright (c) 2024, Ecosoft Co., Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import thai_zkt.www.iclock.push_protocol_2 as push2
import thai_zkt.www.iclock.push_protocol_3 as push3
import json

class ZKUser(Document):
	pass


@frappe.whitelist()
def sync(users):

	print("sync:",users)
 
	dt_ZKTerminal = frappe.qb.DocType('ZK Terminal')
	terminals = (
		frappe.qb.from_(dt_ZKTerminal)
			.select(dt_ZKTerminal.name, dt_ZKTerminal.push_version)
	).run(as_dict=True)
 
	for terminal in terminals:
		if terminal.push_version.startswith("3"):
			terminal["push"] = push3
		else:
			terminal["push"] = push2

	user_id_list = json.loads(users)
 
	dt_ZKUser = frappe.qb.DocType('ZK User')
	qb = frappe.qb.update(dt_ZKUser).set(dt_ZKUser.sync_terminal, "")
	qb.where(dt_ZKUser.id.isin(user_id_list)).run()
 
	user_list = (
		frappe.qb.from_(dt_ZKUser)
			.select(dt_ZKUser.id, dt_ZKUser.user_name, dt_ZKUser.password, dt_ZKUser.privilege, dt_ZKUser.group, dt_ZKUser.main_status)
			.where(dt_ZKUser.id.isin(user_id_list))
	).run(as_dict=True)

	for user in user_list:
		if user.get("main_status") == "Add":
			for terminal in terminals:
				terminal.get("push").create_update_user_command(user, terminal.get("name"),True)
				
		elif user.get("main_status") == "Pre Delete":
			for terminal in terminals:
				terminal.get("push").create_delete_user_command(user, terminal.get("name"),True)
    
	return "OK"



@frappe.whitelist()
def predelete(users):
	print("predelete:",users)

	user_id_list = json.loads(users)
 
	dt_ZKUser = frappe.qb.DocType('ZK User')
	qb = frappe.qb.update(dt_ZKUser).set(dt_ZKUser.main_status, "Pre Delete").set(dt_ZKUser.sync_terminal, "")
    
	qb.where(dt_ZKUser.id.isin(user_id_list)).run()

	return "OK"