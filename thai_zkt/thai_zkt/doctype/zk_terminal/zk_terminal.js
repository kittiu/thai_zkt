// Copyright (c) 2024, Ecosoft Co., Ltd. and contributors
// For license information, please see license.txt

// frappe.ui.form.on("ZK Terminal", {
// 	refresh(frm) {

// 	},
// });

function isOldCode(code) {
    var isOld = false;

    frappe.db.count("ZK Terminal", {registry_code : code})
        .then(count => {
            isOld = count > 0;
        })
    
    return isOld;
}

function genNewCode() {
    
    var s = '';
    var randomchar = function() {
        var n = Math.floor(Math.random() * 62);
        if (n < 10) return n; //1-10
        if (n < 36) return String.fromCharCode(n + 55); //A-Z
        return String.fromCharCode(n + 61); //a-z
    }
    while (s.length < 32) s += randomchar();
    return s;
    
}

frappe.ui.form.on("ZK Terminal", {
    
 	onload(frm) {

        var foundNewCode = false;

        while(!foundNewCode) {
            var newCode = genNewCode();

            if (!isOldCode(newCode)) {
                if (frm.is_new()) {
                    frm.set_value('registry_code',newCode);
                }
                foundNewCode = true;
            }
        }
    },

    refresh:function(frm) {
        frm.add_custom_button(__("Clear"), function() {
            frappe.confirm(
                'Are you sure to Clear User in Terminal "'+frm.doc.name+'"?',
                function(){
                    window.close();

                    frappe.call({
                        method: 'thai_zkt.thai_zkt.doctype.zk_terminal.zk_terminal.clear_terminal_user',
                        args: {
                            terminal: frm.doc.name
                        },
                        freeze: true,
                        callback: (r) => {
                            frappe.msgprint("Clear Terminal "+frm.doc.name);
                        },
                        error: (r) => {
                            frappe.msgprint("Error Clear Terminal "+frm.doc.name);
                        }
                    })                    
                },
                function(){
                    window.close();
                }
            )
        }, __("User"));

        frm.add_custom_button(__("Download to Terminal"), function() {
            frappe.confirm(
                'Are you sure to Download User to Terminal "'+frm.doc.name+'"?',
                function(){
                    window.close();

                    frappe.call({
                        method: 'thai_zkt.thai_zkt.doctype.zk_terminal.zk_terminal.download_terminal_user',
                        args: {
                            terminal: frm.doc.name
                        },
                        freeze: true,
                        callback: (r) => {
                            frappe.msgprint("Download to Terminal "+frm.doc.name);
                        },
                        error: (r) => {
                            frappe.msgprint("Error Download to Terminal "+frm.doc.name);
                        }
                    })                    
                },
                function(){
                    window.close();
                }
            )
        }, __("User"));

        frm.add_custom_button(__("Upload to Server"), function() {
            frappe.msgprint(frm.doc.name);
        }, __("User"));
    }

});
