import streamlit as st
import PyPDF2
import docx
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# 🔑 PUT YOUR OPENAI KEY HERE
# -------- TEXT EXTRACTION --------
def extract_text(file):

    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    else:
        return file.read().decode("utf-8")

# -------- CLAUSE SPLIT --------
def split_clauses(text):
    clauses = re.split(r'\n\d+\.', text)
    return [c.strip() for c in clauses if len(c) > 40]

# -------- RISK DETECTION --------
def detect_risk(clauses):

    risks = []
    total_score = 0

    for clause in clauses:

        text = clause.lower()
        risk = "Low"

        # HIGH RISK
        if "indemnity" in text or "indemnify" in text or "liability" in text:
            risk = "High"
            total_score += 30

        # MEDIUM RISK
        elif "penalty" in text:
            risk = "Medium"
            total_score += 20

        elif "terminate" in text:
            risk = "Medium"
            total_score += 15

        elif "renew" in text or "auto" in text:
            risk = "Medium"
            total_score += 10

        risks.append((clause, risk))

    return risks, total_score

# -------- GPT EXPLANATION --------
def explain_clause(text):

    text_lower = text.lower()

    if "indemnity" in text_lower:
        return "This clause makes one party legally responsible for losses, damages, or legal claims."

    elif "penalty" in text_lower:
        return "This clause imposes a financial penalty if someone exits or breaks the agreement."

    elif "renew" in text_lower or "auto" in text_lower:
        return "This clause automatically renews the contract unless cancelled before a deadline."

    elif "terminate" in text_lower:
        return "This clause allows one party to end the contract, which may create sudden business risk."

    else:
        return "This clause defines responsibilities and legal obligations."

# -------- PDF REPORT --------
def generate_pdf(summary):

    file_name = "report.pdf"
    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Contract Summary Report", styles['Title']))
    story.append(Paragraph(summary, styles['Normal']))

    doc.build(story)

    return file_name

# -------- STREAMLIT UI --------
st.title("📄 Contract Risk Analysis Bot (Hackathon MVP)")

file = st.file_uploader("Upload Contract", type=["pdf","docx","txt"])

if file:

    text = extract_text(file)
    st.subheader("Extracted Text Preview")
    st.write(text[:800])

    clauses = split_clauses(text)

    risks, score = detect_risk(clauses)

    st.subheader("Overall Risk Score")
    st.write(score)

    for clause, risk in risks[:5]:

        st.write("### Clause")
        st.write(clause)

        st.write("Risk Level:", risk)

        explanation = explain_clause(clause)
        st.write("Explanation:", explanation)

    if st.button("Generate Summary PDF"):

        summary = "This contract was analyzed using AI risk detection."
        pdf_file = generate_pdf(summary)

        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF", f, file_name="report.pdf")