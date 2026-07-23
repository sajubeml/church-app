"""
St. Gregorios Orthodox Syrian Church, Mysuru
--------------------------------------------
Excel Workbook (.xlsm) to JSON Converter (Python Native)
Replaces convert_xlsm_data.ps1
"""

import os
import json
import zipfile
import xml.etree.ElementTree as ET

XLSM_PATH = "working Church_Accounting_ok ind updte 21-7-(26-27).xlsm"
OUTPUT_DIR = "data_export"

def convert_xlsm_to_json():
    if not os.path.exists(XLSM_PATH):
        print(f"Error: {XLSM_PATH} not found!")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Reading {XLSM_PATH}...")

    with zipfile.ZipFile(XLSM_PATH, 'r') as z:
        # Load shared strings
        shared_strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            with z.open("xl/sharedStrings.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()
                # Namespaces
                ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                for si in root.findall('main:si', ns):
                    # Combine all text fragments
                    texts = si.findall('.//main:t', ns)
                    shared_strings.append("".join([t.text for t in texts if t.text is not None] if texts else (si.text or "")))

        # Load workbook relationships
        wb_rels = {}
        if "xl/_rels/workbook.xml.rels" in z.namelist():
            with z.open("xl/_rels/workbook.xml.rels") as f:
                tree = ET.parse(f)
                for rel in tree.getroot():
                    r_id = rel.attrib.get('Id')
                    target = rel.attrib.get('Target')
                    if r_id and target:
                        wb_rels[r_id] = target

        # Parse sheets
        if "xl/workbook.xml" in z.namelist():
            with z.open("xl/workbook.xml") as f:
                tree = ET.parse(f)
                ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
                
                sheets = tree.findall('.//main:sheet', ns)
                summary = []

                for sheet in sheets:
                    sheet_name = sheet.attrib.get('name')
                    rel_id = sheet.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                    target = wb_rels.get(rel_id, "")
                    sheet_path = "xl/" + target.lstrip('/')

                    if sheet_path in z.namelist():
                        with z.open(sheet_path) as sf:
                            stree = ET.parse(sf)
                            sroot = stree.getroot()
                            
                            grid = []
                            row_count = 0
                            
                            for row in sroot.findall('.//main:row', ns):
                                row_count += 1
                                row_data = {}
                                for c in row.findall('main:c', ns):
                                    cell_ref = c.attrib.get('r')
                                    cell_type = c.attrib.get('t')
                                    v_elem = c.find('main:v', ns)
                                    val = v_elem.text if v_elem is not None else None

                                    if cell_type == "s" and val is not None:
                                        idx = int(val)
                                        if idx < len(shared_strings):
                                            val = shared_strings[idx]

                                    row_data[cell_ref] = val
                                grid.append(row_data)

                            safe_name = "".join([c if c.isalnum() or c == '_' else '_' for c in sheet_name])
                            json_file = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
                            
                            with open(json_file, "w", encoding="utf-8") as out:
                                json.dump(grid, out, indent=2, ensure_ascii=False)

                            summary.append((sheet_name, row_count, json_file))

                print("\nSheet Extraction Summary:")
                print(f"{'Sheet Name':<25} | {'Rows':<6} | {'JSON Path'}")
                print("-" * 65)
                for name, count, path in summary:
                    print(f"{name:<25} | {count:<6} | {path}")

    print(f"\nSuccessfully extracted all sheets to {OUTPUT_DIR}/")

if __name__ == "__main__":
    convert_xlsm_to_json()
