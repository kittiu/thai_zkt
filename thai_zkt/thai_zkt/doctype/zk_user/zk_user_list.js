frappe.listview_settings['ZK User'] = {
    hide_name_column: true,   

	onload: function(listview) {
        /*
        listview.page.add_inner_button("Sync", function() {
        });
        */

        // listview.page.add_action_item(__("Terminals: Delete ZK Users"), function(){
        //     frappe.confirm(
        //         'Are you sure to Delete Selected ZK Users from All Terminals?',
        //         function(){
        //             // window.close();
        //             listview.disable_list_update = true;
        //             frappe.call({
        //                 method: 'thai_zkt.thai_zkt.doctype.zk_user.zk_user.predelete',
        //                 args: {
        //                     users: listview.get_checked_items(true)
        //                 },
        //                 freeze: true,
        //                 callback: (r) => {
        //                     console.log(listview)
        //                     listview.disable_list_update = false;
        //                     window.location.reload();
        //                 },
        //                 error: (r) => {
        //                     frappe.msgprint("Error : "+r);
        //                 }
        //             })                    
        //         },
        //         // function(){
        //         //     window.close();
        //         // }
        //     )
        // });

        listview.page.add_action_item(__("Terminals : Sync"), function(){
            frappe.confirm(
                'Are you sure to Sync Selected Users to All Terminals?',
                function(){
                    // window.close();

                    listview.disable_list_update = true;

                    frappe.call({
                        method: 'thai_zkt.thai_zkt.doctype.zk_user.zk_user.sync',
                        args: {
                            users: listview.get_checked_items(true)
                        },
                        freeze: true,
                        callback: (r) => {
                            listview.disable_list_update = false;
                            listview.refresh();
                        },
                        error: (r) => {
                            frappe.msgprint("Error : "+r);
                        }
                    })                    
                },
                // function(){
                //     window.close();
                // }
            )
        });
	},
};