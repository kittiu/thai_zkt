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

});
