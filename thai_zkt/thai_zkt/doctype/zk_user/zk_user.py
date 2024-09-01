# Copyright (c) 2024, Ecosoft Co., Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import thai_zkt.www.iclock.push_protocol_2 as push2
import thai_zkt.www.iclock.push_protocol_3 as push3
# from thai_zkt.www.iclock.service import map_user_employee
import json


class ZKUser(Document):
	
	def on_update(self):	
		# Sync to all terminal after insert or update
		old_doc = self.get_doc_before_save()
		if old_doc and old_doc.main_status == self.main_status:
			frappe.db.set_value("ZK User", self.name, "main_status", "Add")
			frappe.db.set_value("ZK User", self.name, "sync_terminal", "")
		if self.main_status in ["Add", "Pre Delete"]:
			sync('["' + self.name + '"]')
		self.reload()
		# Map ZK User with Employee
		map_field = frappe.conf.zkt_usr_mapping_field
		employee = frappe.get_all(
			"Employee",
			filters={
				map_field: ["in", (self.id, self.user_name)],
			},
			pluck="name",
			limit=1,
		)
		if employee:
			frappe.db.set_value("Employee", employee[0], "attendance_device_id", self.id)

	def on_trash(self):
		# Delete all linked document first
		self.delete_linked_docs("ZK Bio Photo")
		self.delete_linked_docs("ZK Bio Data")
		# Delete by zk command Pre Delete, instead of normal delete
		predelete('["' + self.name + '"]')
	
	def delete_linked_docs(self, doctype):
		linked_docs = frappe.get_all(doctype, filters={'zk_user': self.name}, pluck="name")
		for linked_doc in linked_docs:
			linked_doc_doc = frappe.get_doc(doctype, linked_doc)
			linked_doc_doc.delete()


@frappe.whitelist()
def sync(users):

	print("sync:",users)

	dt_ZKTerminal = frappe.qb.DocType('ZK Terminal')
	terminals = (
		frappe.qb.from_(dt_ZKTerminal)
			.select(dt_ZKTerminal.name, dt_ZKTerminal.push_version)
	).run(as_dict=True)
 
	for terminal in terminals:
		if terminal["push_version"].startswith("3"):
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

	# Immediately sync to all terminal
	sync(users)

	return "OK"