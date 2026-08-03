import sys
import os

try:
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    print("index.html read successfully, length:", len(html))

    with open("app.js", "r", encoding="utf-8") as f:
        js = f.read()
    print("app.js read successfully, length:", len(js))

    with open("data.js", "r", encoding="utf-8") as f:
        data_js = f.read()
    print("data.js read successfully, length:", len(data_js))

    with open("html2pdf.bundle.min.js", "r", encoding="utf-8") as f:
        h2p = f.read()
    print("html2pdf.bundle.min.js read successfully, length:", len(h2p))

except Exception as e:
    print("ERROR:", e)
