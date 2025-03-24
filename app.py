import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')  # Use 'gemini-pro' or another available model

# Function to extract text from PDF
def pdf_to_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# Function to calculate match score using Gemini
def calculate_match_score(job_description, resume_text):
    prompt = f"""
    Act as an HR expert. Compare the following job description and resume text.
    Calculate a matching score (0-100%) based on skills, experience, and qualifications.
    Return the score as a single number.

    Job Description: {job_description}
    Resume Text: {resume_text}
    """
    response = model.generate_content(prompt)
    try:
        score = float(response.text.strip())
        return score
    except ValueError:
        return "Error: Could not parse score from Gemini response."

# Function to get resume details using Gemini
def get_resume_details(resume_text):
    prompt = f"""
    Extract and summarize key details from the following resume text.
    Provide the output in this format:
    - Skills: [list skills]
    - Experience: [summarize experience]
    - Education: [summarize education]

    Resume Text: {resume_text}
    """
    response = model.generate_content(prompt)
    return response.text

# Function to suggest questions using Gemini
def suggest_questions(job_description, resume_text):
    prompt = f"""
    As an HR expert, suggest 3-5 interview questions based on the following job description and resume.
    Ensure the questions are specific to the candidate's experience and the job requirements.

    Job Description: {job_description}
    Resume Text: {resume_text}
    """
    response = model.generate_content(prompt)
    return response.text.split('\n')

# Streamlit UI
st.title("ResumeMatch AI - Powered by Google Gemini")

# Input job description
job_description = st.text_area("Paste Job Description Here", height=200)

# Upload resume
uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

# Analyze button
if st.button("Analyze"):
    if not job_description or not uploaded_file:
        st.error("Please provide both job description and resume.")
    else:
        # Extract resume text
        resume_text = pdf_to_text(uploaded_file)

        # Calculate matching score
        score = calculate_match_score(job_description, resume_text)
        st.subheader(f"Matching Score: {score}%")

        # Resume details button
        if st.button("Resume Details"):
            details = get_resume_details(resume_text)
            st.write("### Resume Details")
            st.write(details)

        # Suggested questions
        st.subheader("Suggested Interview Questions")
        questions = suggest_questions(job_description, resume_text)
        for q in questions:
            if q.strip():
                st.write(f"- {q.strip()}")

# Run the app with: streamlit run this_file.py
