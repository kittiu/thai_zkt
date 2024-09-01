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

function addBtnGetInfo(frm,menu_name) {
    frm.add_custom_button(__("Get Server Info"), function() {
        frappe.call({
            method: 'thai_zkt.thai_zkt.doctype.zk_terminal.zk_terminal.get_terminal_info',
            args: {
                terminal: frm.doc.name
            },
            freeze: true,
            callback: (r) => {
                frappe.msgprint("Get Options from Terminal "+frm.doc.name);
            },
            error: (r) => {
                frappe.msgprint("Error : "+frm.doc.name);
            }
        })                    
    }, __(menu_name));
}

function addBtnClearUsers(frm,menu_name) {
    frm.add_custom_button(__("Clear All Terminal Users"), function() {
        frappe.confirm(
            'Are you sure to Clear Users in Terminal "'+frm.doc.name+'"?',
            function(){
                window.close();

                frappe.call({
                    method: 'thai_zkt.thai_zkt.doctype.zk_terminal.zk_terminal.clear_terminal_user',
                    args: {
                        terminal: frm.doc.name
                    },
                    freeze: true,
                    callback: (r) => {
                        frappe.msgprint("Clear Users in Terminal "+frm.doc.name);
                    },
                    error: (r) => {
                        frappe.msgprint("Error : "+frm.doc.name);
                    }
                })                    
            },
            function(){
                window.close();
            }
        )
    }, __(menu_name));
}

function addBtnSetUsers(frm,menu_name) {
    frm.add_custom_button(__("Push All Users to Terminal"), function() {
        frappe.confirm(
            'Are you sure to Push Users to Terminal "'+frm.doc.name+'"?',
            function(){
                window.close();

                frappe.call({
                    method: 'thai_zkt.thai_zkt.doctype.zk_terminal.zk_terminal.download_terminal_user',
                    args: {
                        terminal: frm.doc.name
                    },
                    freeze: true,
                    callback: (r) => {
                        frappe.msgprint("Set Users to Terminal "+frm.doc.name);
                    },
                    error: (r) => {
                        frappe.msgprint("Error : "+frm.doc.name);
                    }
                })                    
            },
            function(){
                window.close();
            }
        )
    }, __(menu_name));
}

function addBtnGetUsers(frm,menu_name) {
    frm.add_custom_button(__("Pull All Users from Terminal"), function() {
        frappe.confirm(
            'Are you sure to Pull Users from Terminal "'+frm.doc.name+'"?',
            function(){
                window.close();

                frappe.call({
                    method: 'thai_zkt.thai_zkt.doctype.zk_terminal.zk_terminal.upload_terminal_user',
                    args: {
                        terminal: frm.doc.name
                    },
                    freeze: true,
                    callback: (r) => {
                        frappe.msgprint("Get Users from Terminal "+frm.doc.name);
                    },
                    error: (r) => {
                        frappe.msgprint("Error : "+frm.doc.name);
                    }
                })                    
            },
            function(){
                window.close();
            }
        )
    }, __(menu_name));
}

function addBtnCmpWithSvr(frm,menu_name) {
    frm.add_custom_button(__("Compare Users With Server"), function() {
        frappe.confirm(
            'Are you sure to Compare User in Terminal '+frm.doc.name+' with Server?',
            function(){

                frm.zk_data = null;
                frm.dashboard.reset();

                window.close();

                frappe.call({
                    method: 'thai_zkt.thai_zkt.doctype.zk_terminal.zk_terminal.compare_user',
                    args: {
                        terminal: frm.doc.name
                    },
                    freeze: true,
                    callback: (r) => {
                        //frappe.msgprint("Compare User in Terminal "+frm.doc.name);
                    },
                    error: (r) => {
                        frappe.msgprint("Error : "+frm.doc.name);
                    }
                })                    
            },
            function(){
                window.close();
            }
        )
    }, __(menu_name));
}

frappe.ui.form.on("ZK Terminal", {

    setup(frm) {
        frappe.realtime.on("compare_terminal", (data) => {
            frm.zk_data = data;
            showDashboard(frm);
        });
    },
    
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

        menu_name = "Direct Command"

        addBtnCmpWithSvr(frm,menu_name);
        addBtnGetUsers(frm,menu_name);
        addBtnClearUsers(frm,menu_name);
        addBtnSetUsers(frm,menu_name);
        addBtnGetInfo(frm,menu_name);

        showDashboard(frm);
    }


});

function showDashboard(frm) {

    var data = frm.zk_data;

    if (data) {
        frm.dashboard.reset();
        frm.dashboard.set_headline("Compare with Server");
        frm.dashboard.add_indicator(
            __("Server: User={0}, Bio Data={1}, Bio Photo={2}", [
                    data.s_user_cnt, data.s_biodata_cnt, data.s_biophoto_cnt
            ]),
            "blue"
        );
        frm.dashboard.add_indicator(
            __("Terminal: User={0}, Bio Data={1}, Bio Photo={2}", [
                    data.t_user_cnt, data.t_biodata_cnt, data.t_biophoto_cnt
            ]),
            data.s_user_cnt==data.t_user_cnt && data.s_biodata_cnt==data.t_biodata_cnt && data.s_biophoto_cnt==data.t_biophoto_cnt ? "blue" : "red"
        );
    }
}
