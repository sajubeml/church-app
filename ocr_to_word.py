"""
OCR to Word Converter (Math & Text OCR -> DOCX)
Supports text and math equation extraction with Word OMML Math rendering.
"""

import sys
import os
import re
import argparse
import zipfile
import xml.etree.ElementTree as ET

# Try importing Pillow and PyTesseract / EasyOCR if available
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

def convert_latex_or_text_to_omml(expr):
    """
    Converts plain text or basic LaTeX math expression to Microsoft Word OMML XML format.
    Supports:
    - Superscripts (x^2, x^{10})
    - Subscripts (x_1, x_{n})
    - Fractions (3/x, 1/x, \\frac{a}{b})
    - Standard operations (+, -, *, =, \\pm, \\sqrt)
    """
    expr = expr.strip()
    
    def r_math(text):
        if not text:
            return ""
        # Clean text
        text = text.replace("-", "\u2212").replace("*", "\u00D7")
        return f'<m:r><m:t>{text}</m:t></m:r>'

    def parse_expr(s):
        # Check for fraction like \frac{a}{b} or simple a/b
        frac_match = re.search(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', s)
        if frac_match:
            num, den = frac_match.group(1), frac_match.group(2)
            start, end = frac_match.span()
            before = parse_expr(s[:start])
            after = parse_expr(s[end:])
            frac_xml = f'<m:f><m:num>{parse_expr(num)}</m:num><m:den>{parse_expr(den)}</m:den></m:f>'
            return f'{before}{frac_xml}{after}'
        
        # Simple fraction: single char or simple token / token
        simple_frac = re.search(r'([a-zA-Z0-9]+)/([a-zA-Z0-9]+)', s)
        if simple_frac:
            num, den = simple_frac.group(1), simple_frac.group(2)
            start, end = simple_frac.span()
            before = parse_expr(s[:start])
            after = parse_expr(s[end:])
            frac_xml = f'<m:f><m:num>{parse_expr(num)}</m:num><m:den>{parse_expr(den)}</m:den></m:f>'
            return f'{before}{frac_xml}{after}'

        # Check for superscripts like x^2 or x^{2}
        sup_match = re.search(r'([a-zA-Z0-9]+)\^(\{([^{}]+)\}|([a-zA-Z0-9]+))', s)
        if sup_match:
            base = sup_match.group(1)
            sup = sup_match.group(3) or sup_match.group(4)
            start, end = sup_match.span()
            before = parse_expr(s[:start])
            after = parse_expr(s[end:])
            sup_xml = f'<m:sSup><m:e>{r_math(base)}</m:e><m:sup>{r_math(sup)}</m:sup></m:sSup>'
            return f'{before}{sup_xml}{after}'

        return r_math(s)

    inner_xml = parse_expr(expr)
    return f'<m:oMath>{inner_xml}</m:oMath>'


def create_word_docx(lines, output_filename="OCR_Output.docx", title="OCR Document Output"):
    """
    Creates a Word (.docx) file containing text and editable math equations.
    """
    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
    <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
    <Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
</Types>"""

    package_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    word_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
    <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
    <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>
</Relationships>"""

    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:docDefaults>
        <w:rPrDefault>
            <w:rPr>
                <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                <w:sz w:val="24"/>
            </w:rPr>
        </w:rPrDefault>
    </w:docDefaults>
</w:styles>"""

    settings_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:mathPr>
        <m:mathFont xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" m:val="Cambria Math"/>
    </w:mathPr>
</w:settings>"""

    font_table_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fontTable xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:font w:name="Calibri"/>
    <w:font w:name="Cambria Math"/>
</w:fontTable>"""

    document_body = []

    # Title
    document_body.append(f"""
    <w:p>
        <w:pPr>
            <w:pStyle w:val="Heading1"/>
        </w:pPr>
        <w:r>
            <w:rPr>
                <w:b/>
                <w:sz w:val="36"/>
                <w:color w:val="1F4E78"/>
            </w:rPr>
            <w:t>{title}</w:t>
        </w:r>
    </w:p>
    """)

    for item in lines:
        if isinstance(item, str):
            # Regular text line or formula detection
            if any(char in item for char in ['^', '=', '\\', '/']) and len(re.findall(r'[x0-9]', item)) > 1:
                # Math Equation
                omml = convert_latex_or_text_to_omml(item)
                document_body.append(f"""
                <w:p>
                    <w:pPr>
                        <w:ind w:left="360"/>
                    </w:pPr>
                    <w:r><w:t>• </w:t></w:r>
                    {omml}
                </w:p>
                """)
            else:
                # Normal Text
                document_body.append(f"""
                <w:p>
                    <w:r>
                        <w:t>{item}</w:t>
                    </w:r>
                </w:p>
                """)

    body_xml = "".join(document_body)
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
    <w:body>
        {body_xml}
    </w:body>
</w:document>"""

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', content_types_xml)
        docx.writestr('_rels/.rels', package_rels_xml)
        docx.writestr('word/_rels/document.xml.rels', word_rels_xml)
        docx.writestr('word/document.xml', document_xml)
        docx.writestr('word/styles.xml', styles_xml)
        docx.writestr('word/settings.xml', settings_xml)
        docx.writestr('word/fontTable.xml', font_table_xml)

    print(f"Created Word Document: {os.path.abspath(output_filename)}")

def perform_ocr(image_path):
    """
    Performs OCR on an image file. Returns extracted text lines.
    """
    if not HAS_PIL:
        raise ImportError("Pillow library is required for image processing. Install via: pip install Pillow")

    img = Image.open(image_path)

    if HAS_TESSERACT:
        print("Performing Tesseract OCR...")
        text = pytesseract.image_to_string(img)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return lines
    else:
        print("Tesseract OCR package not detected. Please install pytesseract/tesseract or use the web interface.")
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCR image and export to Word (.docx)")
    parser.add_argument("--image", help="Path to input image file")
    parser.add_argument("--output", default="OCR_Output.docx", help="Output Word document path (.docx)")

    args = parser.parse_args()

    if args.image:
        lines = perform_ocr(args.image)
        if lines:
            create_word_docx(lines, args.output)
    else:
        print("No image provided. Run with --image <path> or use generate_doc.py to generate sample.")
