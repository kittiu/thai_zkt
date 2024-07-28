import frappe
import datetime
from frappe.query_builder import Criterion

@frappe.whitelist(methods=["POST"])
def delete_terminal_option(zk_terminal):
    
    frappe.db.delete("ZK Terminal Option", {
        "zk_terminal": zk_terminal
    })
    
    return "OK"


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
