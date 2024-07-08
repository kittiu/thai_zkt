import frappe

@frappe.whitelist(methods=["POST", "GET"])
def delete_terminal_option(zk_terminal):
    
    frappe.db.delete("ZK Terminal Option", {
        "zk_terminal": zk_terminal
    })
    
    return "OK"