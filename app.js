/**
 * St. Gregorios Church Accounting Application Logic
 * Implements VBA UserForm (frmEntry) behavior, 2-way member sync,
 * Document Type selection (Receipt vs Payment Voucher),
 * Cash/Bank safety lock, side-by-side receipt generator, Excel Date formatting, and ledger views.
 */

// Application State
const state = {
  members: [],
  cashbook: [],
  individual: [],
  trialBalance: [],
  codes: [],
  auction: [],
  cart: [],
  currentReceiptNo: 4001,
  currentVoucherNo: 1
};

// Helper to extract column value regardless of cell key format ("B" or "B2" or "B3")
function getColVal(rowObj, colLetter) {
  if (!rowObj) return "";
  if (rowObj[colLetter] !== undefined && rowObj[colLetter] !== null) return String(rowObj[colLetter]).trim();
  const targetKey = Object.keys(rowObj).find(k => k.toUpperCase().replace(/[0-9]/g, '') === colLetter.toUpperCase());
  return (targetKey && rowObj[targetKey] !== null) ? String(rowObj[targetKey]).trim() : "";
}

// Convert Excel Serial Date Number (e.g. 46113) or ISO Date to DD-MM-YYYY format
function formatExcelDate(val) {
  if (!val) return "";
  const str = String(val).trim();

  // If it's a 5-digit number (Excel Serial Date e.g. 46113)
  if (/^\d{5}$/.test(str)) {
    const serial = parseInt(str);
    // Excel epoch 1899-12-30 offset in days to 1970-01-01 is 25569
    const utcDays = serial - 25569;
    const date = new Date(utcDays * 86400 * 1000);
    const day = String(date.getUTCDate()).padStart(2, '0');
    const month = String(date.getUTCMonth() + 1).padStart(2, '0');
    const year = date.getUTCFullYear();
    return `${day}-${month}-${year}`;
  }

  // If already formatted like YYYY-MM-DD
  if (/^\d{4}-\d{2}-\d{2}$/.test(str)) {
    const parts = str.split('-');
    return `${parts[2]}-${parts[1]}-${parts[0]}`;
  }

  return str;
}

// Currency formatter - avoids ₹ NaN
function formatCurrency(val) {
  if (val === null || val === undefined || val === "") return "";
  const cleaned = String(val).replace(/[^0-9.-]/g, '');
  if (!cleaned) return "";
  const num = parseFloat(cleaned);
  if (isNaN(num)) return "";
  return "₹ " + num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// ----------------------------------------------------
// 1. INDIAN RUPEE NUMBER TO WORDS (VBA SpellNumberINR)
// ----------------------------------------------------
function numberToIndianWords(amount) {
  const val = parseFloat(amount);
  if (isNaN(val) || val <= 0) return "Zero Rupees Only";

  const rupees = Math.floor(val);
  const paisa = Math.round((val - rupees) * 100);

  const units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
                 "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
                 "Seventeen", "Eighteen", "Nineteen"];
  const tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"];

  function belowThousand(n) {
    let w = "";
    if (n >= 100) {
      w += units[Math.floor(n / 100)] + " Hundred ";
      n %= 100;
    }
    if (n >= 20) {
      w += tens[Math.floor(n / 10)] + (n % 10 !== 0 ? " " + units[n % 10] : "");
    } else if (n > 0) {
      w += units[n];
    }
    return w.trim();
  }

  function convert(n) {
    if (n === 0) return "Zero";
    const crore = Math.floor(n / 10000000); n %= 10000000;
    const lakh = Math.floor(n / 100000); n %= 100000;
    const thousand = Math.floor(n / 1000); n %= 1000;

    let res = [];
    if (crore > 0) res.push(belowThousand(crore) + " Crore");
    if (lakh > 0) res.push(belowThousand(lakh) + " Lakh");
    if (thousand > 0) res.push(belowThousand(thousand) + " Thousand");
    if (n > 0) res.push(belowThousand(n));
    return res.join(" ");
  }

  const rStr = rupees > 0 ? convert(rupees) + " Rupees" : "Zero Rupees";
  const pStr = paisa > 0 ? " and " + convert(paisa) + " Paisa" : "";
  return `${rStr}${pStr} Only`;
}

// ----------------------------------------------------
// 2. DATA INITIALIZATION & LOAD (File & Server Offline Support)
// ----------------------------------------------------
document.addEventListener("DOMContentLoaded", async () => {
  await loadAllData();
  setupNavigation();
  setupFormEventListeners();
  renderAllViews();
});

async function loadAllData() {
  try {
    // 1. First try window.CHURCH_DATA (synchronous, 0-CORS file:// support)
    if (window.CHURCH_DATA) {
      state.members = window.CHURCH_DATA.members || [];
      state.cashbook = window.CHURCH_DATA.cashbook || [];
      state.individual = window.CHURCH_DATA.individual || [];
      state.trialBalance = window.CHURCH_DATA.trialBalance || [];
      state.codes = window.CHURCH_DATA.codes || [];
      state.auction = window.CHURCH_DATA.auction || [];
      console.log("Loaded data synchronously from embedded window.CHURCH_DATA!");
    } else {
      // 2. Fallback to fetch API
      const fetchJson = async (name) => {
        const res = await fetch(`data_export/${name}.json`);
        return res.ok ? await res.json() : [];
      };

      state.members = await fetchJson("Members");
      state.cashbook = await fetchJson("Cash_Book");
      state.individual = await fetchJson("Individual");
      state.trialBalance = await fetchJson("Trial_Balance");
      state.codes = await fetchJson("Codes");
      state.auction = await fetchJson("aution25");
    }

    calculateNextNumbers();
    populateMemberDropdown();
  } catch (err) {
    console.error("Data load error:", err);
  }
}

function calculateNextNumbers() {
  let maxR = 4000;
  let maxV = 0;
  state.cashbook.forEach(row => {
    const rVal = getColVal(row, "B");
    const vVal = getColVal(row, "L");
    if (rVal && !isNaN(parseInt(rVal))) {
      const r = parseInt(rVal);
      if (r > maxR) maxR = r;
    }
    if (vVal && !isNaN(parseInt(vVal))) {
      const v = parseInt(vVal);
      if (v > maxV) maxV = v;
    }
  });
  state.currentReceiptNo = maxR + 1;
  state.currentVoucherNo = maxV + 1;

  updateDocTypeView();
  document.getElementById("txtDate").valueAsDate = new Date();
}

// Populate Member Dropdown from ALL worksheets (Individual, Members, Auction)
function populateMemberDropdown() {
  const cmbMember = document.getElementById("cmbMember");
  cmbMember.innerHTML = `<option value="">-- Select Member --</option>`;

  const memberMap = new Map();
  const invalidNames = ["NAME OF HOF", "NAME", "SL. NO.", "REGISTER NO.", "REGISTER NO", "SL NO", "MEMBER NAME"];

  // 1. Load from Individual Sheet (Col B = Reg No, Col C = Name of HoF)
  state.individual.forEach(row => {
    const regNo = getColVal(row, "B");
    const name = getColVal(row, "C");
    if (regNo && name && !invalidNames.includes(regNo.toUpperCase()) && !invalidNames.includes(name.toUpperCase())) {
      memberMap.set(regNo, name);
    }
  });

  // 2. Load from Members Sheet (Col B = Register No, Col C = Name)
  state.members.forEach(row => {
    const regNo = getColVal(row, "B");
    const name = getColVal(row, "C");
    if (regNo && name && !invalidNames.includes(regNo.toUpperCase()) && !invalidNames.includes(name.toUpperCase())) {
      if (!memberMap.has(regNo)) {
        memberMap.set(regNo, name);
      }
    }
  });

  // Sort by Register Number numerically
  const sortedRegNos = Array.from(memberMap.keys()).sort((a, b) => {
    const numA = parseInt(a) || 0;
    const numB = parseInt(b) || 0;
    return numA - numB;
  });

  sortedRegNos.forEach(regNo => {
    const name = memberMap.get(regNo);
    const opt = document.createElement("option");
    opt.value = regNo;
    opt.textContent = `Reg #${regNo} - ${name}`;
    opt.dataset.name = name;
    cmbMember.appendChild(opt);
  });

  console.log(`Successfully populated ${sortedRegNos.length} parish members into dropdown.`);
}

// ----------------------------------------------------
// 3. NAVIGATION TAB SWITCHING
// ----------------------------------------------------
function setupNavigation() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      tab.classList.add("active");
      const paneId = tab.dataset.tab;
      document.getElementById(paneId).classList.add("active");
    });
  });
}

// ----------------------------------------------------
// 4. FORM SETUP & 2-WAY MEMBER SYNC
// ----------------------------------------------------
function setupFormEventListeners() {
  const cmbMember = document.getElementById("cmbMember");

  // 2-Way Sync: Member Select -> Reg No
  cmbMember.addEventListener("change", (e) => {
    const regNo = e.target.value;
    document.getElementById("txtRegNo").value = regNo;
  });

  // 2-Way Sync: Reg No Input -> Member Select
  document.getElementById("txtRegNo").addEventListener("input", (e) => {
    const regNo = e.target.value.trim();
    cmbMember.value = regNo;
  });

  // Document Type Change (Receipt vs Payment Voucher)
  document.getElementById("optDocReceipt").addEventListener("change", updateDocTypeView);
  document.getElementById("optDocVoucher").addEventListener("change", updateDocTypeView);

  // Account Head Code Select Listener
  document.getElementById("cmbAccountHead").addEventListener("change", (e) => {
    document.getElementById("txtCode").value = e.target.value;
  });

  // Payment Type Lock (Cash XOR Bank)
  const optCash = document.getElementById("optCash");
  const optBank = document.getElementById("optBank");
  const txtCashAmt = document.getElementById("txtCashAmt");
  const txtBankAmt = document.getElementById("txtBankAmt");

  optCash.addEventListener("change", () => {
    txtCashAmt.disabled = false;
    txtBankAmt.disabled = true;
    txtBankAmt.value = "";
    txtCashAmt.focus();
  });

  optBank.addEventListener("change", () => {
    txtBankAmt.disabled = false;
    txtBankAmt.disabled = true;
    txtCashAmt.value = "";
    txtBankAmt.focus();
  });

  // Add Item to Cart
  document.getElementById("btnAddItem").addEventListener("click", addItemToCart);

  // Clear Form
  document.getElementById("btnClearForm").addEventListener("click", clearForm);

  // Generate Receipt / Voucher Modal
  document.getElementById("btnGenerateReceipt").addEventListener("click", showReceiptModal);
}

function updateDocTypeView() {
  const isReceipt = document.getElementById("optDocReceipt").checked;
  const numLabel = document.getElementById("lblNum");
  const txtNum = document.getElementById("txtVoucherNo");
  const cmbHead = document.getElementById("cmbAccountHead");
  const btnGen = document.getElementById("btnGenerateReceipt");

  cmbHead.innerHTML = `<option value="">-- Select Account Head --</option>`;

  if (isReceipt) {
    numLabel.textContent = "Receipt No.";
    txtNum.value = state.currentReceiptNo;
    btnGen.textContent = "🖨️ Generate & Print Dual Receipt (Original + Copy)";

    const receiptHeads = [
      { code: "RP-3.82", name: "Monthly Subscription (Current Year)" },
      { code: "RP-3.83", name: "Monthly Subscription (Previous Year)" },
      { code: "RP-2.02", name: "Catholicate Day & Recessa" },
      { code: "RP-2.03", name: "Metropolitan Fund" },
      { code: "RP-2.04", name: "Mission Sunday" },
      { code: "RP-2.05", name: "Seminary Day" },
      { code: "RP-2.06", name: "Priest Welfare Fund" },
      { code: "RP-2.13", name: "Passion Week Collection" },
      { code: "RP-2.14", name: "St. Gregorios Feast (Annual Feast)" },
      { code: "RP-2.15", name: "Parish Day / Harvest Collection" },
      { code: "RP-2.16", name: "Christmas / New Year Collection" },
      { code: "RP-2.17", name: "Perunnal Vanchika (House Offertory Box)" },
      { code: "RP-2.18", name: "St. George Feast" },
      { code: "RP-2.19", name: "St. Thomas Feast" },
      { code: "RP-2.20", name: "St. Mary's Feast" },
      { code: "RP-10.01", name: "Auction Dues - Old" },
      { code: "RP-10.02", name: "Auction Current" },
      { code: "RP-2.01", name: "General Donations" }
    ];

    receiptHeads.forEach(h => {
      const opt = document.createElement("option");
      opt.value = h.code;
      opt.textContent = `[${h.code}] ${h.name}`;
      opt.dataset.name = h.name;
      cmbHead.appendChild(opt);
    });
  } else {
    numLabel.textContent = "Voucher No.";
    txtNum.value = state.currentVoucherNo;
    btnGen.textContent = "🖨️ Generate & Print Payment Voucher";

    const paymentHeads = [
      { code: "RP-16.06", name: "Passion Week Expenses" },
      { code: "RP-19.31", name: "Salary Quota to Diocese (Vicar)" },
      { code: "RP-12.03(a)", name: "Salary to Sexton" },
      { code: "RP-16.01", name: "Church Maintenance & Repairs" },
      { code: "RP-16.02", name: "Electricity & Water Charges" },
      { code: "RP-16.03", name: "Altar & Holy Qurbana Supplies" },
      { code: "RP-16.04", name: "Parish Feast Expenses" },
      { code: "RP-16.05", name: "Charity & Relief Expenses" },
      { code: "RP-19.01", name: "Diocese Quota & Assessment" },
      { code: "RP-20.01", name: "Printing & Stationery" }
    ];

    paymentHeads.forEach(h => {
      const opt = document.createElement("option");
      opt.value = h.code;
      opt.textContent = `[${h.code}] ${h.name}`;
      opt.dataset.name = h.name;
      cmbHead.appendChild(opt);
    });
  }
}

function addItemToCart() {
  const cmbHead = document.getElementById("cmbAccountHead");
  const code = cmbHead.value;
  const name = cmbHead.options[cmbHead.selectedIndex]?.dataset.name || "";
  const details = document.getElementById("txtDetails").value.trim();

  const isCash = document.getElementById("optCash").checked;
  const cashAmt = parseFloat(document.getElementById("txtCashAmt").value) || 0;
  const bankAmt = parseFloat(document.getElementById("txtBankAmt").value) || 0;
  const amount = isCash ? cashAmt : bankAmt;

  // Validation
  if (!code) {
    alert("SAFETY ERROR: Please select an Account Head!");
    return;
  }
  if (amount <= 0) {
    alert("SAFETY ERROR: Please enter a valid amount!");
    return;
  }

  state.cart.push({
    code,
    particulars: name,
    details,
    paymentType: isCash ? "Cash" : "Bank",
    amount
  });

  renderCartTable();
  
  // Clear item fields
  cmbHead.value = "";
  document.getElementById("txtCode").value = "";
  document.getElementById("txtDetails").value = "";
  document.getElementById("txtCashAmt").value = "";
  document.getElementById("txtBankAmt").value = "";
}

function renderCartTable() {
  const tbody = document.getElementById("cartTbody");
  tbody.innerHTML = "";

  let grandTotal = 0;

  state.cart.forEach((item, index) => {
    grandTotal += item.amount;
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="text-center">${index + 1}</td>
      <td><strong>[${item.code}]</strong> ${item.particulars}</td>
      <td>${item.details || '-'}</td>
      <td class="text-center"><span class="header-badge" style="background:#e2e8f0; color:#334155;">${item.paymentType}</span></td>
      <td class="text-right">₹ ${item.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
      <td class="text-center"><button class="btn btn-outline" style="padding:2px 8px; color:var(--danger-color);" onclick="removeCartItem(${index})">✕</button></td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById("cartTotalAmt").textContent = `₹ ${grandTotal.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
  document.getElementById("cartTotalWords").textContent = numberToIndianWords(grandTotal);
}

function removeCartItem(index) {
  state.cart.splice(index, 1);
  renderCartTable();
}

function clearForm() {
  state.cart = [];
  renderCartTable();
  document.getElementById("txtRegNo").value = "";
  document.getElementById("cmbMember").value = "";
  document.getElementById("txtDetails").value = "";
}

// ----------------------------------------------------
// 5. DUAL SIDE-BY-SIDE PRINTABLE RECEIPT MODAL
// ----------------------------------------------------
function showReceiptModal() {
  if (state.cart.length === 0) {
    alert("Please add at least one item to the cart!");
    return;
  }

  const isReceipt = document.getElementById("optDocReceipt").checked;
  const docTitle = isReceipt ? "RECEIPT" : "PAYMENT VOUCHER";
  const numLabel = isReceipt ? "Receipt No" : "Voucher No";
  const docNo = document.getElementById("txtVoucherNo").value;
  const dateStr = document.getElementById("txtDate").value;
  const regNo = document.getElementById("txtRegNo").value;
  const cmbMember = document.getElementById("cmbMember");
  
  let memberName = "General / N/A";
  if (cmbMember.selectedIndex > 0) {
    memberName = cmbMember.options[cmbMember.selectedIndex].dataset.name || cmbMember.options[cmbMember.selectedIndex].text;
  }

  let grandTotal = 0;
  let itemRowsHtml = "";

  state.cart.forEach((item, idx) => {
    grandTotal += item.amount;
    itemRowsHtml += `
      <tr>
        <td style="text-align:center;">${idx + 1}</td>
        <td>${item.particulars} (${item.code})</td>
        <td style="text-align:right;">₹ ${item.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
      </tr>
    `;
  });

  const totalWords = numberToIndianWords(grandTotal);

  const receiptContent = `
    <div style="display:flex; gap:20px; flex-wrap:wrap;">
      <!-- ORIGINAL -->
      <div style="flex:1; border:2px solid #1e293b; border-radius:8px; padding:15px; background:#fff; min-width:320px; position:relative;">
        <span style="position:absolute; right:12px; top:12px; background:#10b981; color:#fff; font-size:10px; font-weight:bold; padding:2px 8px; border-radius:4px;">ORIGINAL</span>
        <div style="text-align:center; border-bottom:2px solid #1e293b; padding-bottom:8px; margin-bottom:12px;">
          <h3 style="margin:0; font-size:15px; color:#0f172a;">ST. GREGORIOS ORTHODOX SYRIAN CHURCH</h3>
          <p style="margin:2px 0; font-size:11px; color:#64748b;">Government House Road, Nazarbad, Mysuru, Karnataka 570 010</p>
          <p style="font-weight:bold; font-size:12px; color:#1e293b; margin-top:4px;">${docTitle}</p>
        </div>
        <table style="width:100%; margin-bottom:10px; font-size:12px;">
          <tr><td><strong>${numLabel}:</strong> #${docNo}</td><td style="text-align:right;"><strong>Date:</strong> ${dateStr}</td></tr>
          <tr><td><strong>Register No:</strong> ${regNo || 'N/A'}</td><td style="text-align:right;"><strong>Party / Member:</strong> ${memberName}</td></tr>
        </table>
        <table style="width:100%; border-collapse:collapse; margin-bottom:12px; font-size:12px;">
          <thead>
            <tr style="background:#f8fafc;"><th style="border:1px solid #cbd5e1; padding:6px; text-align:center;">#</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:left;">Particulars</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:right;">Amount</th></tr>
          </thead>
          <tbody>${itemRowsHtml}</tbody>
        </table>
        <div style="background:#f1f5f9; padding:8px; border-radius:4px; font-size:12px; font-weight:bold; margin-bottom:25px;">
          <div>Total: ₹ ${grandTotal.toLocaleString('en-IN', {minimumFractionDigits: 2})}</div>
          <div style="font-size:11px; font-weight:normal; font-style:italic; margin-top:2px;">(${totalWords})</div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:bold; color:#64748b;">
          <div>Prepared By: ________</div>
          <div>Trustee / Treasurer: ________</div>
        </div>
      </div>

      <!-- DUPLICATE COPY -->
      <div style="flex:1; border:2px solid #1e293b; border-radius:8px; padding:15px; background:#fff; min-width:320px; position:relative;">
        <span style="position:absolute; right:12px; top:12px; background:#f59e0b; color:#fff; font-size:10px; font-weight:bold; padding:2px 8px; border-radius:4px;">COPY</span>
        <div style="text-align:center; border-bottom:2px solid #1e293b; padding-bottom:8px; margin-bottom:12px;">
          <h3 style="margin:0; font-size:15px; color:#0f172a;">ST. GREGORIOS ORTHODOX SYRIAN CHURCH</h3>
          <p style="margin:2px 0; font-size:11px; color:#64748b;">Government House Road, Nazarbad, Mysuru, Karnataka 570 010</p>
          <p style="font-weight:bold; font-size:12px; color:#1e293b; margin-top:4px;">${docTitle} (OFFICE COPY)</p>
        </div>
        <table style="width:100%; margin-bottom:10px; font-size:12px;">
          <tr><td><strong>${numLabel}:</strong> #${docNo}</td><td style="text-align:right;"><strong>Date:</strong> ${dateStr}</td></tr>
          <tr><td><strong>Register No:</strong> ${regNo || 'N/A'}</td><td style="text-align:right;"><strong>Party / Member:</strong> ${memberName}</td></tr>
        </table>
        <table style="width:100%; border-collapse:collapse; margin-bottom:12px; font-size:12px;">
          <thead>
            <tr style="background:#f8fafc;"><th style="border:1px solid #cbd5e1; padding:6px; text-align:center;">#</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:left;">Particulars</th><th style="border:1px solid #cbd5e1; padding:6px; text-align:right;">Amount</th></tr>
          </thead>
          <tbody>${itemRowsHtml}</tbody>
        </table>
        <div style="background:#f1f5f9; padding:8px; border-radius:4px; font-size:12px; font-weight:bold; margin-bottom:25px;">
          <div>Total: ₹ ${grandTotal.toLocaleString('en-IN', {minimumFractionDigits: 2})}</div>
          <div style="font-size:11px; font-weight:normal; font-style:italic; margin-top:2px;">(${totalWords})</div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:bold; color:#64748b;">
          <div>Prepared By: ________</div>
          <div>Trustee / Treasurer: ________</div>
        </div>
      </div>
    </div>
  `;

  document.getElementById("receiptModalArea").innerHTML = receiptContent;
  document.getElementById("receiptModal").classList.add("active");
}

function closeReceiptModal() {
  document.getElementById("receiptModal").classList.remove("active");
}

// ----------------------------------------------------
// 6. RENDER ALL DATA VIEWS
// ----------------------------------------------------
function renderAllViews() {
  renderCashbook();
  renderIndividualLedgers();
  renderTrialBalance();
  renderAudit();
}

function renderCashbook() {
  const tbody = document.getElementById("cashbookTbody");
  tbody.innerHTML = "";

  state.cashbook.forEach(row => {
    const dtRaw = getColVal(row, "A");
    const payDtRaw = getColVal(row, "K");
    const recNo = getColVal(row, "B");
    const regNo = getColVal(row, "C");
    const hof = getColVal(row, "D");
    let head = getColVal(row, "E");
    const code = getColVal(row, "F");
    const details = getColVal(row, "G");
    const cashR = getColVal(row, "H");
    const bankR = getColVal(row, "I");
    const payHead = getColVal(row, "M");
    const cashP = getColVal(row, "P");
    const bankP = getColVal(row, "Q");

    // Skip top header rows
    if (recNo.toLowerCase().includes("receipt") || dtRaw.toLowerCase().includes("date") || dtRaw.toLowerCase().includes("cash book")) {
      return;
    }

    // Label Opening Balance explicitly
    let isOpening = false;
    if (details.toLowerCase().includes("opening balance") || (!head && (getColVal(row, "H") == "9879" || getColVal(row, "I") == "651682"))) {
      head = "Opening Balance";
      isOpening = true;
    }

    const displayDate = formatExcelDate(dtRaw || payDtRaw);

    if (displayDate || recNo || head || payHead || cashR || bankR || cashP || bankP) {
      const tr = document.createElement("tr");
      if (isOpening) tr.style.background = "#f0fdf4";

      tr.innerHTML = `
        <td><strong>${displayDate}</strong></td>
        <td><strong>${recNo ? '#' + recNo : ''}</strong></td>
        <td>${regNo}</td>
        <td>${hof}</td>
        <td>${isOpening ? '<span class="header-badge" style="background:#dcfce7; color:#15803d; font-weight:700;">Opening Balance</span>' : head}</td>
        <td><code>${code}</code></td>
        <td class="text-right">${formatCurrency(cashR)}</td>
        <td class="text-right">${formatCurrency(bankR)}</td>
        <td>${payHead}</td>
        <td class="text-right">${formatCurrency(cashP)}</td>
        <td class="text-right">${formatCurrency(bankP)}</td>
      `;
      tbody.appendChild(tr);
    }
  });
}

function renderIndividualLedgers() {
  const tbody = document.getElementById("indivTbody");
  tbody.innerHTML = "";

  state.individual.forEach(row => {
    const sl = getColVal(row, "A");
    const regNo = getColVal(row, "B");
    const name = getColVal(row, "C");
    const subUpto = getColVal(row, "D");
    const sub = getColVal(row, "E");
    const cath = getColVal(row, "G");
    const metro = getColVal(row, "H");
    const pass = getColVal(row, "V");
    const auct = getColVal(row, "AH");
    const grand = getColVal(row, "AM");

    if (regNo && regNo !== "Register No." && regNo !== "Register No" && name !== "Name of HoF") {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="text-center">${sl}</td>
        <td><strong>Reg #${regNo}</strong></td>
        <td>${name}</td>
        <td>${subUpto}</td>
        <td class="text-right">${formatCurrency(sub)}</td>
        <td class="text-right">${formatCurrency(cath)}</td>
        <td class="text-right">${formatCurrency(metro)}</td>
        <td class="text-right">${formatCurrency(pass)}</td>
        <td class="text-right">${formatCurrency(auct)}</td>
        <td class="text-right" style="font-weight:bold; color:var(--accent-color);">${formatCurrency(grand)}</td>
      `;
      tbody.appendChild(tr);
    }
  });
}

function renderTrialBalance() {
  const tbody = document.getElementById("tbTbody");
  tbody.innerHTML = "";

  state.trialBalance.forEach(row => {
    const rCode = getColVal(row, "A");
    const rHead = getColVal(row, "B");
    const rAmt = getColVal(row, "C");
    const pCode = getColVal(row, "D");
    const pHead = getColVal(row, "E");
    const pAmt = getColVal(row, "F");

    if ((rHead || pHead) && rHead !== "Account Head" && pHead !== "Account Head") {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><code>${rCode}</code></td>
        <td>${rHead}</td>
        <td class="text-right">${formatCurrency(rAmt)}</td>
        <td><code>${pCode}</code></td>
        <td>${pHead}</td>
        <td class="text-right">${formatCurrency(pAmt)}</td>
      `;
      tbody.appendChild(tr);
    }
  });
}

function renderAudit() {
  let openingCash = 9879.00;
  let openingBank = 651682.00;
  let totalCashR = 0, totalBankR = 0, totalCashP = 0, totalBankP = 0;

  state.cashbook.forEach(row => {
    const details = getColVal(row, "G").toLowerCase();
    const head = getColVal(row, "E").toLowerCase();
    const payHead = getColVal(row, "M").toLowerCase();
    const h = getColVal(row, "H");
    const i = getColVal(row, "I");
    const p = getColVal(row, "P");
    const q = getColVal(row, "Q");

    // Ignore opening balance row from income calculation
    if (details.includes("opening balance") || (!head && (h == "9879" || i == "651682"))) {
      return;
    }

    // Ignore contra transfers
    if (head.includes("contra") || payHead.includes("contra") || details.includes("contra") || details.includes("cash deposit") || head.includes("deposit to bank")) {
      return;
    }

    if (h && !isNaN(parseFloat(h))) totalCashR += parseFloat(h) || 0;
    if (i && !isNaN(parseFloat(i))) totalBankR += parseFloat(i) || 0;
    if (p && !isNaN(parseFloat(p))) totalCashP += parseFloat(p) || 0;
    if (q && !isNaN(parseFloat(q))) totalBankP += parseFloat(q) || 0;
  });

  const openingTotal = openingCash + openingBank;
  const grandR = totalCashR + totalBankR;
  const grandP = totalCashP + totalBankP;
  const netClosingBalance = openingTotal + grandR - grandP;

  document.getElementById("auditTotalR").textContent = formatCurrency(grandR) || "₹ 0.00";
  document.getElementById("auditTotalP").textContent = formatCurrency(grandP) || "₹ 0.00";
  document.getElementById("auditNetBal").textContent = formatCurrency(netClosingBalance) || "₹ 0.00";
  document.getElementById("auditMembers").textContent = document.querySelectorAll("#cmbMember option").length - 1;
}
