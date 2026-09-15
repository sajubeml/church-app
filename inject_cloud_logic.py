import os

app_js_path = r"c:\saju_old pc\Church_App\anti_gravity\app_cloud.js"

cloud_override_code = """

// ==========================================
// CLOUD OVERRIDE LOGIC
// ==========================================
console.log("Cloud Mode Initialized");

// Override loadAllData to fetch from api.php
const originalLoadAllData = window.loadAllData || async function() {};

window.loadAllData = async function() {
    console.log("Loading data from cloud database...");
    try {
        const response = await fetch('https://orthodoxchurchmysore.in/api/api.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'action=get_cashbook'
        });
        
        const result = await response.json();
        if (result.success && result.data) {
            state.cashbook = result.data;
            console.log("Cloud Cashbook Loaded:", state.cashbook.length, "rows");
        }
    } catch (e) {
        console.error("Cloud fetch error:", e);
    }
    
    // Attempt original load logic for other JSONs as fallback
    try {
        await originalLoadAllData();
    } catch (e) {}
};

// Override AndroidBridge save logic to save to api.php
if (typeof window.AndroidBridge === 'undefined') {
    window.AndroidBridge = {};
}

window.AndroidBridge.saveTransaction = function(jsonStr, isReceipt) {
    console.log("Saving transaction to cloud:", jsonStr);
    try {
        const obj = JSON.parse(jsonStr);
        // Transform the object for the API
        let apiParams = new URLSearchParams();
        apiParams.append('action', 'add_cashbook');
        
        if (isReceipt) {
            apiParams.append('date', obj.date || '');
            apiParams.append('receipt_no', obj.receipt_no || '');
            apiParams.append('reg_no', obj.reg_no || '');
            apiParams.append('name_of_hof', obj.name_of_hof || '');
            apiParams.append('receipt_acct_head', obj.receipt_acct_head || '');
            apiParams.append('receipt_code', obj.receipt_code || '');
            apiParams.append('receipt_details', obj.receipt_details || '');
            apiParams.append('receipt_cash', obj.receipt_cash || '0');
            apiParams.append('receipt_bank', obj.receipt_bank || '0');
            apiParams.append('payment_cash', '0');
            apiParams.append('payment_bank', '0');
        } else {
            apiParams.append('date', obj.payment_date || '');
            apiParams.append('receipt_no', obj.payment_voucher_no || '');
            apiParams.append('payment_acct_head', obj.payment_acct_head || '');
            apiParams.append('payment_code', obj.payment_code || '');
            apiParams.append('payment_details', obj.payment_details || '');
            apiParams.append('payment_cash', obj.payment_cash || '0');
            apiParams.append('payment_bank', obj.payment_bank || '0');
            apiParams.append('receipt_cash', '0');
            apiParams.append('receipt_bank', '0');
        }
        
        fetch('https://orthodoxchurchmysore.in/api/api.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: apiParams.toString()
        }).then(res => res.json()).then(result => {
            console.log("Cloud save result:", result);
        });
        return true;
    } catch (e) {
        console.error("Cloud save error:", e);
        return false;
    }
};

window.AndroidBridge.bulkSync = function(jsonStr) {
    console.log("Bulk sync to cloud triggered");
    // Implementation for bulk sync
    return true;
};
"""

with open(app_js_path, "a", encoding="utf-8") as f:
    f.write(cloud_override_code)

print("Injected cloud override logic into app_cloud.js")
