import os
import zipfile
import xml.etree.ElementTree as ET

def create_quadratic_word_doc(filename="Quadratic_Example1.docx"):
    # Content Types XML
    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
    <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
    <Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
</Types>"""

    # Package Relationships XML
    package_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    # Word Relationships XML
    word_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
    <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
    <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>
</Relationships>"""

    # Word Styles XML
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

    # Word Settings XML
    settings_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:mathPr>
        <m:mathFont xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" m:val="Cambria Math"/>
        <m:brkBin xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" m:val="before"/>
    </w:mathPr>
</w:settings>"""

    # Word Font Table XML
    font_table_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fontTable xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:font w:name="Calibri"/>
    <w:font w:name="Cambria Math"/>
</w:fontTable>"""

    # OMML Math Helpers
    # Equation 1: 3x^2 - 5x + 2 = 0
    # Equation 2: 2x^2 + 5x = 0
    # Equation 3: x^2 + 3/x = 5
    # Equation 4: 2x - 1/x = 3
    # Equation 5: 3x^2 - 4x + 1 = 3x^2 - 3x + 4

    def r_math(text):
        return f'<m:r><m:t>{text}</m:t></m:r>'

    def sup_math(base_text, sup_text):
        return f'<m:sSup><m:e>{r_math(base_text)}</m:e><m:sup>{r_math(sup_text)}</m:sup></m:sSup>'

    def frac_math(num_text, den_text):
        return f'<m:f><m:num>{r_math(num_text)}</m:num><m:den>{r_math(den_text)}</m:den></m:f>'

    eq1_omml = f'<m:oMath>{r_math("3")}{sup_math("x", "2")}{r_math(" \u2212 5x + 2 = 0")}</m:oMath>'
    eq2_omml = f'<m:oMath>{r_math("2")}{sup_math("x", "2")}{r_math(" + 5x = 0")}</m:oMath>'
    eq3_omml = f'<m:oMath>{sup_math("x", "2")}{r_math(" + ")}{frac_math("3", "x")}{r_math(" = 5")}</m:oMath>'
    eq4_omml = f'<m:oMath>{r_math("2x \u2212 ")}{frac_math("1", "x")}{r_math(" = 3")}</m:oMath>'
    eq5_omml = f'<m:oMath>{r_math("3")}{sup_math("x", "2")}{r_math(" \u2212 4x + 1 = 3")}{sup_math("x", "2")}{r_math(" \u2212 3x + 4")}</m:oMath>'

    eqs = [eq1_omml, eq2_omml, eq3_omml, eq4_omml, eq5_omml]

    document_body_items = []

    # Title
    document_body_items.append("""
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
                <w:jc w:val="left"/>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="36"/>
                    <w:color w:val="1F4E78"/>
                </w:rPr>
                <w:t>Quadratic Equations - OCR Export</w:t>
            </w:r>
        </w:p>
    """)

    # Subtitle / Description
    document_body_items.append("""
        <w:p>
            <w:r>
                <w:rPr>
                    <w:i/>
                    <w:color w:val="595959"/>
                </w:rPr>
                <w:t>The Word file has the recognized questions with proper math equation formatting:</w:t>
            </w:r>
        </w:p>
    """)

    # Bullet list with Math Equations
    for eq in eqs:
        document_body_items.append(f"""
        <w:p>
            <w:pPr>
                <w:pStyle w:val="ListBullet"/>
                <w:ind w:left="720" w:hanging="360"/>
            </w:pPr>
            <w:r>
                <w:t>•  </w:t>
            </w:r>
            {eq}
        </w:p>
        """)

    # Footer note
    document_body_items.append("""
        <w:p>
            <w:pPr>
                <w:spacing w:before="240"/>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:b/>
                    <w:color w:val="2E75B6"/>
                </w:rPr>
                <w:t>You can now edit, print, or add solutions directly in Word.</w:t>
            </w:r>
        </w:p>
    """)

    body_xml = "".join(document_body_items)

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
    <w:body>
        {body_xml}
    </w:body>
</w:document>"""

    # Zip into .docx
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', content_types_xml)
        docx.writestr('_rels/.rels', package_rels_xml)
        docx.writestr('word/_rels/document.xml.rels', word_rels_xml)
        docx.writestr('word/document.xml', document_xml)
        docx.writestr('word/styles.xml', styles_xml)
        docx.writestr('word/settings.xml', settings_xml)
        docx.writestr('word/fontTable.xml', font_table_xml)

    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    create_quadratic_word_doc()
