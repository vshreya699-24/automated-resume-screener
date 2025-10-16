import pdfplumber, docx2txt

def extract_text_from_file(file_path):
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            return " ".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif file_path.endswith(".docx"):
        return docx2txt.process(file_path)
    else:
        return ""