frappe.listview_settings['ZK User'] = {
	onload: function(listview) {
        /*
        listview.page.add_inner_button("Sync", function() {
        });
        */

        listview.page.add_action_item(__("Terminals : Pre Delete"), function(){
            frappe.confirm(
                'Are you sure to Pre Delete Selected Users from All Terminals?',
                function(){
                    window.close();

                    listview.disable_list_update = true;
    
                    frappe.call({
                        method: 'thai_zkt.thai_zkt.doctype.zk_user.zk_user.predelete',
                        args: {
                            users: listview.get_checked_items(true)
                        },
                        freeze: true,
                        callback: (r) => {
                            listview.disable_list_update = false;
//                            this.clear_checked_items();
                            listview.refresh();

                            frappe.msgprint("Pre Delete Selected Users","Terminals : Pre Delete");
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

        listview.page.add_action_item(__("Terminals : Sync"), function(){
            frappe.confirm(
                'Are you sure to Sync Selected Users to All Terminals?',
                function(){
                    window.close();

                    listview.disable_list_update = true;

                    frappe.call({
                        method: 'thai_zkt.thai_zkt.doctype.zk_user.zk_user.sync',
                        args: {
                            users: listview.get_checked_items(true)
                        },
                        freeze: true,
                        callback: (r) => {
                            listview.disable_list_update = false;
//                            this.clear_checked_items();
                            listview.refresh();
                            
                            frappe.msgprint("Sync Selected Users to All Terminals","Terminals : Sync");
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