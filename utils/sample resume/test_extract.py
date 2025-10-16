from utils.extract_text import extract_text_from_file
import os

# update name below to the resume file you put in resumes/
resume_filename = "sample_resume.pdf"   # or "sample_resume.docx"
resume_path = os.path.join("resumes", resume_filename)

if not os.path.exists(resume_path):
    print(f"ERROR: file not found -> {resume_path}")
else:
    text = extract_text_from_file(resume_path)
    if not text:
        print("No text was extracted (empty string). Possible reasons: file is empty, encrypted, or extractor failed.")
    else:
        print("=== Extracted text preview (first 800 chars) ===\n")
        print(text[:800])                # show preview
        print("\n---")
        print(f"Total characters extracted: {len(text)}")