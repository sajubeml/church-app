async function startBulkPdfExport() {
  if (typeof state === 'undefined' || !state.individual || !state.cashbook) {
    alert("Data not loaded yet. Please wait.");
    return;
  }
  
  if (typeof JSZip === 'undefined') {
    alert("JSZip library not loaded!");
    return;
  }
  
  const btn = document.getElementById('bulkZipPdfBtn');
  if (btn) {
    btn.disabled = true;
    btn.innerText = "Processing... (This may take a minute)";
  }

  try {
    const indRows = state.individual;
    const cbEntries = state.cashbook;
    const headerRow = indRows[3] || {};
    
    const memberMap = {};
    
    for (let i = 4; i < indRows.length; i++) {
      const r = indRows[i];
      const sl = String(r.A || '').trim();
      const reg = String(r.B || '').trim();
      const name = String(r.C || '').trim();
      const subUpto = String(r.D || '').trim();
      
      if (!reg && !name) continue;
      if (reg === 'GRAND TOTAL' || name === 'GRAND TOTAL') continue;
      
      const isNm = (reg.toUpperCase() === 'NM' || reg.toUpperCase() === 'NON MEMBER' || reg.toUpperCase() === 'NON-MEMBER' || reg === '' ||
                    reg.toUpperCase().includes('NM') || name.toUpperCase().includes('NON MEMBER') || name.toUpperCase().includes('- NM'));
      if (isNm) continue;
      
      if (!memberMap[reg]) {
        memberMap[reg] = {
          sl: sl, reg: reg, name: name, sub_upto: subUpto, summary_heads: {}, receipt_transactions: [], total: 0
        };
      }
      
      const m = memberMap[reg];
      for (const k in headerRow) {
        if (['A','B','C','D','AM'].includes(k)) continue;
        const hName = headerRow[k];
        let valStr = String(r[k] || '').replace(/,/g, '').trim();
        let val = parseFloat(valStr);
        if (isNaN(val)) val = 0;
        if (val > 0) {
          m.summary_heads[hName] = (m.summary_heads[hName] || 0) + val;
        }
      }
    }
    
    for (let i = 0; i < cbEntries.length; i++) {
      const r = cbEntries[i];
      const date = String(r.A || '').trim();
      const rec_no = String(r.B || '').trim();
      const reg_no = String(r.C || '').trim();
      const name = String(r.D || '').trim();
      const head = String(r.E || '').trim();
      const code = String(r.F || '').trim();
      const details = String(r.G || '').trim();
      const amt_h = String(r.H || '').replace(/,/g, '').trim();
      const amt_i = String(r.I || '').replace(/,/g, '').trim();
      
      let cashAmt = parseFloat(amt_h); if(isNaN(cashAmt)) cashAmt = 0;
      let bankAmt = parseFloat(amt_i); if(isNaN(bankAmt)) bankAmt = 0;
      let totAmt = cashAmt + bankAmt;
      
      if (memberMap[reg_no] && totAmt > 0) {
        memberMap[reg_no].receipt_transactions.push({
          date: date, rec_no: rec_no, head: head, code: code, details: details, amount: totAmt
        });
      }
    }
    
    const activePayingMembers = {};
    for (const reg in memberMap) {
      const m = memberMap[reg];
      if (m.receipt_transactions.length > 0) {
        m.total = m.receipt_transactions.reduce((sum, t) => sum + t.amount, 0);
      } else {
        m.total = Object.values(m.summary_heads).reduce((sum, val) => sum + val, 0);
      }
      if (m.total > 0) {
        activePayingMembers[reg] = m;
      }
    }
    
    const zip = new JSZip();
    const usedFilenames = new Set();
    
    const opt = {
      margin: [10, 10, 10, 10], // mm
      filename: 'temp.pdf',
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, allowTaint: true, logging: false, backgroundColor: '#ffffff' },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak: { mode: ['css', 'legacy'] }
    };

    const d = new Date();
    const currentDateStr = `${String(d.getDate()).padStart(2,'0')}-${String(d.getMonth()+1).padStart(2,'0')}-${d.getFullYear()}`;
    
    const keys = Object.keys(activePayingMembers);
    
    // Process one by one to avoid UI freeze / memory crash
    for (let i = 0; i < keys.length; i++) {
      const reg = keys[i];
      const m = activePayingMembers[reg];
      
      if (btn) {
         btn.innerText = `Generating PDF ${i+1} of ${keys.length}...`;
      }
      
      let cleanName = m.name.replace(/[\\/*?:"<>|]/g, '').trim();
      if (!cleanName) cleanName = `Member_Reg_${reg}`;
      let filename = `${cleanName}.pdf`;
      if (usedFilenames.has(filename)) {
        filename = `${cleanName} (Reg #${reg}).pdf`;
      }
      usedFilenames.add(filename);
      
      const rt_nos = Array.from(new Set(m.receipt_transactions.map(t => t.rec_no).filter(x => x)));
      const rt_str = rt_nos.length > 0 ? rt_nos.sort().join(', ') : `STMT-REG-#${reg}`;
      
      let tableRows = '';
      if (m.receipt_transactions.length > 0) {
         m.receipt_transactions.forEach((tx, idx) => {
           tableRows += `<tr>
             <td>${idx+1}</td>
             <td>${tx.date || '-'}</td>
             <td><b>${tx.rec_no || '-'}</b></td>
             <td><b>${tx.head}</b></td>
             <td>${tx.details || '-'}</td>
             <td><b>₹ ${tx.amount.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</b></td>
           </tr>`;
         });
      } else {
         let idx = 1;
         Object.keys(m.summary_heads).sort().forEach(hName => {
           const amt = m.summary_heads[hName];
           tableRows += `<tr>
             <td>${idx++}</td>
             <td>-</td>
             <td>-</td>
             <td><b>${hName}</b></td>
             <td>-</td>
             <td><b>₹ ${amt.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</b></td>
           </tr>`;
         });
      }
      
      const wrappedHtml = `
      <div style="font-family: Helvetica, Arial, sans-serif; padding: 20px; color: #2D3748;">
        <div style="display: flex; align-items: center; border-bottom: 2px solid #1A365D; padding-bottom: 15px; margin-bottom: 20px;">
           <img src="${(typeof window !== 'undefined' && window.CHURCH_LOGO_BASE64) ? window.CHURCH_LOGO_BASE64 : 'church_logo.png'}" style="width: 60px; height: 60px; margin-right: 15px;" onerror="this.style.display='none'">
           <div>
             <div style="font-size: 18px; font-weight: bold; color: #1A365D;">ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE</div>
             <div style="font-size: 11px; color: #4A5568;">Government House Road, Nazarbad, Mysuru, Karnataka — 570010</div>
             <div style="font-size: 13px; font-weight: bold; color: #2B6CB0; margin-top: 5px;">MEMBER CONTRIBUTION STATEMENT & RECEIPT SUMMARY</div>
           </div>
        </div>
        
        <table style="width: 100%; border-collapse: collapse; background: #F7FAFC; border: 1px solid #CBD5E0; margin-bottom: 20px;">
          <tr>
             <td style="padding: 10px; border: 1px solid #E2E8F0; width: 25%;"><b>Register No:</b></td>
             <td style="padding: 10px; border: 1px solid #E2E8F0; width: 25%; color: #2B6CB0;"><b>#${m.reg}</b></td>
             <td style="padding: 10px; border: 1px solid #E2E8F0; width: 25%;"><b>Statement Date:</b></td>
             <td style="padding: 10px; border: 1px solid #E2E8F0; width: 25%;"><b>${currentDateStr}</b></td>
          </tr>
          <tr>
             <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>Member Name:</b></td>
             <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>${m.name}</b></td>
             <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>Rt No. / Ref:</b></td>
             <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>${rt_str}</b></td>
          </tr>
          <tr>
             <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>Subscription Upto:</b></td>
             <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>${m.sub_upto || '-'}</b></td>
             <td style="padding: 10px; border: 1px solid #E2E8F0;"><b>Total Contributions:</b></td>
             <td style="padding: 10px; border: 1px solid #E2E8F0; color: #2F855A; font-size:16px;"><b>₹ ${m.total.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</b></td>
          </tr>
        </table>
        
        <div style="font-size: 14px; font-weight: bold; color: #1A365D; margin-bottom: 10px;">Itemized Receipt Transactions & Contributions:</div>
        
        <table style="width: 100%; border-collapse: collapse; border: 1px solid #CBD5E0; font-size: 12px; margin-bottom: 40px;">
          <thead>
            <tr style="background: #1A365D; color: #ffffff;">
               <th style="padding: 8px; border: 1px solid #E2E8F0;">Sl</th>
               <th style="padding: 8px; border: 1px solid #E2E8F0;">Date</th>
               <th style="padding: 8px; border: 1px solid #E2E8F0;">Rt No.</th>
               <th style="padding: 8px; border: 1px solid #E2E8F0;">Accounts Head / Category</th>
               <th style="padding: 8px; border: 1px solid #E2E8F0;">Details / Remarks</th>
               <th style="padding: 8px; border: 1px solid #E2E8F0;">Amount (₹)</th>
            </tr>
          </thead>
          <tbody>
            ${tableRows}
            <tr style="background: #2B6CB0; color: #ffffff;">
               <td colspan="3" style="padding: 8px; border: 1px solid #E2E8F0;"></td>
               <td style="padding: 8px; border: 1px solid #E2E8F0;"><b>TOTAL MEMBER CONTRIBUTIONS</b></td>
               <td style="padding: 8px; border: 1px solid #E2E8F0;"></td>
               <td style="padding: 8px; border: 1px solid #E2E8F0;"><b>₹ ${m.total.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</b></td>
            </tr>
          </tbody>
        </table>
        
        <table style="width: 100%; border-collapse: collapse; margin-top: 50px;">
           <tr>
             <td style="width: 33%; vertical-align: bottom;">Date: <b>${currentDateStr}</b></td>
             <td style="width: 34%; text-align: center; vertical-align: bottom;">Verified By: Trustee / Vicar</td>
             <td style="width: 33%; text-align: right; vertical-align: bottom;">Authorized Signature & Seal</td>
           </tr>
        </table>
      </div>
      `;
      
      const blob = await html2pdf().set(opt).from(wrappedHtml).output('blob');
      zip.file(filename, blob);
    }
    
    if (btn) {
      btn.innerText = "Zipping Files... Please wait.";
    }
    
    const zipContent = await zip.generateAsync({type:"blob"});
    const url = URL.createObjectURL(zipContent);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Individual_Member_PDF_Statements_${currentDateStr}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    if (btn) {
      btn.innerText = "Export All Member PDFs (ZIP)";
      btn.disabled = false;
    }
    
  } catch (err) {
    console.error("Error generating bulk PDFs:", err);
    alert("Error generating PDFs: " + err.message + "\n" + (err.stack ? err.stack.substring(0, 100) : ""));
    if (btn) {
      btn.innerText = "Export All Member PDFs (ZIP)";
      btn.disabled = false;
    }
  }
}
window.startBulkPdfExport = startBulkPdfExport;
