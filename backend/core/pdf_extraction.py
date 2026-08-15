import io, re
from PyPDF2 import PdfReader

def _text(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_composition_from_pdf(pdf_bytes):
    text = _text(pdf_bytes)
    out = {}
    for el in ["Al","Al2O3","Si","Fe","Mg","Cu","Zn","Mn","Ni","Ca","Na","K","Ti"]:
        m = re.search(rf"\b{re.escape(el)}\b\s*[:=,-]?\s*(\d+(?:\.\d+)?)\s*%?", text, re.I)
        if m:
            out[el] = float(m.group(1))
    return out

def extract_sds_sections(pdf_bytes):
    text = _text(pdf_bytes)
    sections = {}
    for n in range(1,17):
        pat = rf"(?:SECTION|Section)\s*{n}\s*[:\-]?\s*(.*?)(?=(?:SECTION|Section)\s*{n+1}\s*[:\-]?|\Z)"
        m = re.search(pat, text, re.S)
        if m:
            sections[str(n)] = m.group(1).strip()[:5000]
    return sections

def get_sds_product_name(pdf_bytes):
    text = _text(pdf_bytes)
    m = re.search(r"(?:Product name|Product identifier)\s*[:\-]\s*(.+)", text, re.I)
    return m.group(1).strip() if m else None
