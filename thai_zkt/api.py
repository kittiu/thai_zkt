import frappe
import datetime
from frappe.query_builder import Criterion

@frappe.whitelist(methods=["POST"])
def update_command_list_status(cmd_id_list, status):
    
    dt_ZKCommand = frappe.qb.DocType('ZK Command')
    
    qb = frappe.qb.update(dt_ZKCommand).set(dt_ZKCommand.status, status)
    
    if status == "Sent":
        now = datetime.datetime.now()
        date_field = frappe.qb.Field("sent_time")
        qb.set(date_field, now.__str__())
    elif status == "Done":
        now = datetime.datetime.now()
        date_field = frappe.qb.Field('done_time')
        qb.set(date_field, now.__str__())
    
    #cmd_criterions = [dt_ZKCommand.id == cmd_id for cmd_id in cmd_id_list] 
    #qb.where(Criterion.any(cmd_criterions)).run()
    qb.where(dt_ZKCommand.id.isin(cmd_id_list)).run()

    return "OK"


@frappe.whitelist(methods=["GET"])
def count_terminal():
    return frappe.db.count('ZK Terminal')


@frappe.whitelist(methods=["DELETE"])
def delete_user(pin):
    
    dt_ZKBioPhoto = frappe.qb.DocType('ZK Bio Photo')
    qb = frappe.qb.from_(dt_ZKBioPhoto).where(dt_ZKBioPhoto.zk_user == pin).delete().run()

    dt_ZKBioData = frappe.qb.DocType('ZK Bio Data')
    qb = frappe.qb.from_(dt_ZKBioData).where(dt_ZKBioData.zk_user == pin).delete().run()

    frappe.delete_doc("ZK User", pin)
