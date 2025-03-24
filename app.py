import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    st.warning("python-dotenv not installed. Ensure it's in requirements.txt and environment variables are set manually.")

# Set page title to "SkillSync AI"
st.set_page_config(page_title="SkillSync AI", page_icon="🤖", layout="wide")

# Load API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY not found. Please set it in your environment variables.")
    st.stop()  # Halt execution if no API key
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

# Function to extract text from PDF
def pdf_to_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# Function to calculate match score using Gemini with temperature
def calculate_match_score(job_description, resume_text):
    prompt = f"""
    Act as an HR expert. Compare the following job description and resume text.
    Calculate a matching score (0-100%) based on skills, experience, and qualifications.
    Return the score as a single number.

    Job Description: {job_description}
    Resume Text: {resume_text}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2)  # Low temperature for consistency
        )
        score = float(response.text.strip())
        return score
    except Exception as e:
        st.error(f"Error calculating match score: {e}")
        return None

# Function to get resume details using Gemini with temperature
def get_resume_details(resume_text):
    prompt = f"""
    Extract and summarize key details from the following resume text.
    Provide the output in this format:
    - Skills: [list skills]
    - Experience: [summarize experience]
    - Education: [summarize education]

    Resume Text: {resume_text}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2)  # Low temperature for consistency
        )
        return response.text
    except Exception as e:
        st.error(f"Error fetching resume details: {e}")
        return "Unable to retrieve details."

# Function to suggest questions using Gemini with temperature
def suggest_questions(job_description, resume_text):
    prompt = f"""
    As an HR expert, suggest 3-5 interview questions based on the following job description and resume.
    Ensure the questions are specific to the candidate's experience and the job requirements.

    Job Description: {job_description}
    Resume Text: {resume_text}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2)  # Low temperature for consistency
        )
        return response.text.split('\n')
    except Exception as e:
        st.error(f"Error suggesting questions: {e}")
        return ["Unable to generate questions."]

# Streamlit UI
st.title("SkillSync AI")
st.write("Powered by Google Gemini")

# Input job description
job_description = st.text_area("Paste Job Description Here", height=200)

# Upload resume
uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

# Store resume text in session state to persist across interactions
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None

# Resume Details button (moved first)
if st.button("Resume Details"):
    if uploaded_file:
        if not st.session_state.resume_text:
            st.session_state.resume_text = pdf_to_text(uploaded_file)
        details = get_resume_details(st.session_state.resume_text)
        st.subheader("Resume Details")
        st.markdown(details)
    else:
        st.error("Please upload a resume first.")

# Analyze button (moved second)
if st.button("Analyze"):
    if not job_description or not uploaded_file:
        st.error("Please provide both job description and resume.")
    else:
        # Extract and store resume text if not already done
        if not st.session_state.resume_text:
            st.session_state.resume_text = pdf_to_text(uploaded_file)
        resume_text = st.session_state.resume_text

        # Calculate matching score
        score = calculate_match_score(job_description, resume_text)
        if score is not None:
            st.subheader(f"Matching Score: {score}%")

        # Suggested questions
        st.subheader("Suggested Interview Questions")
        questions = suggest_questions(job_description, resume_text)
        for q in questions:
            if q.strip():
                st.write(f"- {q.strip()}")

# Run the app with: streamlit run this_file.py
