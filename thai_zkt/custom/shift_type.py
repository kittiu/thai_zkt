import frappe

def update_last_sync_of_checkin():
	docs = frappe.db.get_all(
		"Shift Type",
		pluck="name"
	)
	for doc_name in docs:
		frappe.db.set_value(
			"Shift Type",
			doc_name,
			"last_sync_of_checkin",
			frappe.utils.now()
		)
