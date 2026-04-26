import sys
import zipfile
import xml.etree.ElementTree as ET

def extract_text_from_docx(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as zf:
            xml_content = zf.read('word/document.xml')
        
        tree = ET.fromstring(xml_content)
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        texts = []
        for paragraph in tree.findall('.//w:p', namespaces):
            para_text = []
            for run in paragraph.findall('.//w:r', namespaces):
                t = run.find('.//w:t', namespaces)
                if t is not None and t.text:
                    para_text.append(t.text)
            if para_text:
                texts.append(''.join(para_text))
        return '\n'.join(texts)
    except Exception as e:
        return str(e)

if len(sys.argv) > 1:
    print(extract_text_from_docx(sys.argv[1]))
