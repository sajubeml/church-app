import subprocess
import os

test_html = os.path.abspath("scratch/test.html")
os.makedirs("scratch", exist_ok=True)

with open(test_html, "w", encoding="utf-8") as f:
    f.write("<html><body><h1>ST GREGORIOS CHURCH TEST RECEIPT</h1></body></html>")

out_pdf = os.path.abspath("scratch/Receipt_TEST.pdf")

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

cmd = [edge_path, "--headless", f"--print-to-pdf={out_pdf}", "--no-pdf-header-footer", test_html]
print("Running command:", cmd)
res = subprocess.run(cmd, capture_output=True, text=True)
print("Exit code:", res.returncode)
print("PDF created:", os.path.exists(out_pdf))
if os.path.exists(out_pdf):
    print("PDF File Size:", os.path.getsize(out_pdf), "bytes")
