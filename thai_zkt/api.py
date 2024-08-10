import frappe
import json
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
    qb.where(dt_ZKCommand.name.isin(cmd_id_list)).run()

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


@frappe.whitelist(methods=["GET"])
def count_user(serial_number):
    print("count_user()")
    print("serial_number:",serial_number)

    user_cnt = frappe.db.count('ZK User')
    biodata_cnt = frappe.db.count('ZK Bio Data')
    biophoto_cnt = frappe.db.count('ZK Bio Photo')

    dt_ZKCommand = frappe.qb.DocType('ZK Command')
    cmds = (
		frappe.qb.from_(dt_ZKCommand)
			.select(dt_ZKCommand.name, dt_ZKCommand.command, dt_ZKCommand.after_done)
			.where(dt_ZKCommand.terminal == serial_number)
			.where(dt_ZKCommand.status == "Sent")
  			.where(dt_ZKCommand.command.like("DATA COUNT%"))
   			.where(dt_ZKCommand.after_done.like("%save_count%"))
	).run(as_dict=True)

    print("cmds:",cmds)

    t_user_cnt = -1
    t_biodata_cnt = -1
    t_biophoto_cnt = -1

    for cmd in cmds:
        command = cmd["command"]
        after_done = json.loads(cmd["after_done"])
        count = after_done["count"]

        print("- command:",command)
        print("- after_done:",after_done)
        print("- count:",count)

        if "user" in command:
            t_user_cnt = count 
        elif "biodata" in command:
            t_biodata_cnt = count
        elif "biophoto" in command:
            t_biophoto_cnt = count

    if len(cmds)==3:
        return dict(user_cnt=user_cnt, biodata_cnt=biodata_cnt, biophoto_cnt=biophoto_cnt, t_user_cnt=t_user_cnt, t_biodata_cnt=t_biodata_cnt, t_biophoto_cnt=t_biophoto_cnt)
    else:
        return 500,"Not 3"
