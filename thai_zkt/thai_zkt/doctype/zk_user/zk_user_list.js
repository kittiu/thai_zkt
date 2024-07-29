frappe.listview_settings['ZK User'] = {
	onload: function(listview) {

        listview.page.add_inner_button("Sync", function() {

            frappe.confirm(
                'Are you sure to Sync Selected Users to All Terminals?',
                function(){
                    window.close();

                    users = listview.get_checked_items(true);
    
                    frappe.call({
                        method: 'thai_zkt.thai_zkt.doctype.zk_user.zk_user.sync',
                        args: {
                            users: users
                        },
                        freeze: true,
                        callback: (r) => {
                            frappe.msgprint("Sync Selected Users to All Terminals");
                        },
                        error: (r) => {
                            frappe.msgprint("Error : "+r);
                        }
                    })                    
                },
                function(){
                    window.close();
                }
            )
        });

	}
};