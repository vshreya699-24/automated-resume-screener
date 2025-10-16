import streamlit as st
import os
import pandas as pd
from datetime import datetime

# Import functions from utils
from utils.extract_text import extract_text_from_file
from utils.scoring import get_match_score
from utils.duplicate_check import get_file_hash
from utils.db_handler import init_db, check_six_month_policy
import sqlite3

# Initialize database
init_db()

# Streamlit app title and description
st.set_page_config(page_title="Automated Resume Screener", layout="centered")
st.title("🤖 Automated Resume Screener")
st.write("Upload a Job Description and Resumes to automatically compare and shortlist candidates.")

# -------------------------------
# Step 1: Upload Job Description
# -------------------------------
st.subheader("📄 Step 1: Upload Job Description (JD)")
jd_file = st.file_uploader(
    "Upload JD (.txt, .pdf, .docx)",
    type=["txt", "pdf", "docx"],
    key="jd_upload_box"
)

jd_text = ""
if jd_file:
    jd_path = os.path.join("job_descriptions", jd_file.name)
    with open(jd_path, "wb") as f:
        f.write(jd_file.getbuffer())
    jd_text = extract_text_from_file(jd_path)
    st.success(f"Job Description '{jd_file.name}' uploaded successfully!")

# -------------------------------
# Step 2: Upload Resumes
# -------------------------------
st.subheader("👩‍💻 Step 2: Upload Resumes")
resume_files = st.file_uploader(
    "Upload one or more resumes (.pdf, .docx)",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    key="resume_upload_box"
)

# -------------------------------
# Step 3: Process and Compare
# -------------------------------
if jd_text and resume_files:
    st.subheader("📊 Screening Results")

    results = []
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    for resume in resume_files:
        resume_path = os.path.join("resumes", resume.name)
        with open(resume_path, "wb") as f:
            f.write(resume.getbuffer())

        file_hash = get_file_hash(resume_path)

        # Check for duplicate file
        c.execute("SELECT * FROM applications WHERE file_hash=?", (file_hash,))
        duplicate = c.fetchone()

        if duplicate:
            results.append({
                "Resume": resume.name,
                "Email": "—",
                "Score": "—",
                "Status": "Duplicate",
                "Reason": "Same file uploaded before"
            })
            continue

        # Get resume text
        resume_text = extract_text_from_file(resume_path)

        # Ask for candidate email and company name
        email = st.text_input(f"Enter email for {resume.name}:")
        company = st.text_input(f"Enter company name for {resume.name}:")

        # Check 6-month rejection policy
        if check_six_month_policy(email, company):
            results.append({
                "Resume": resume.name,
                "Email": email,
                "Score": "—",
                "Status": "Auto-Rejected",
                "Reason": "Rejected within last 6 months"
            })
            continue

        # Get similarity score (in percentage)
        score = get_match_score(jd_text, resume_text)

        # Shortlist or reject
        if score >= 60:
            status = "Shortlisted"
            reason = "High JD match"
        else:
            status = "Rejected"
            reason = "Low JD match"

        # Save in database
        date_today = datetime.now().strftime("%Y-%m-%d")
        c.execute(
            "INSERT INTO applications (email, company, job_title, file_hash, score, status, reason, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (email, company, jd_file.name, file_hash, score, status, reason, date_today)
        )
        conn.commit()

        results.append({
            "Resume": resume.name,
            "Email": email,
            "Score": f"{score:.2f}%",
            "Status": status,
            "Reason": reason
        })

    conn.close()

    # Display results
    df = pd.DataFrame(results)
    st.dataframe(df)

    # Export to CSV
    csv_path = "screening_results.csv"
    df.to_csv(csv_path, index=False)
    st.success(f"✅ Results exported to {csv_path}")

else:
    st.info("Please upload both Job Description and at least one Resume to begin screening.")
