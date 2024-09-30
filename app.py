# Import Libraries
from dotenv import load_dotenv
import os
import base64
import io
from PIL import Image
import fitz  # PyMuPDF
import google.generativeai as genai
import streamlit as st

# Load environment variables
load_dotenv()

# Configure Google Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Helper function to get the Gemini response
def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        if pdf_content is not None:
            response = model.generate_content([input_text, pdf_content[0], prompt])
            return response.text
        else:
            return "PDF content is missing. Please upload a valid PDF file."
    except Exception as e:
        return f"Error with Gemini API: {e}"

# Helper function to process PDF and convert to image
def input_pdf_setup(uploaded_file):
    try:
        if uploaded_file:
            pdf = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
            images = [Image.open(io.BytesIO(page.get_pixmap().tobytes())) 
                      for page_num in range(pdf.page_count) 
                      for page in [pdf.load_page(page_num)]]

            if not images:
                st.error("No pages found in the uploaded PDF.")
                return None

            # Convert first page to base64-encoded JPEG
            img_byte_arr = io.BytesIO()
            images[0].save(img_byte_arr, format="JPEG")
            img_byte_arr = img_byte_arr.getvalue()

            pdf_parts = [{
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }]
            return pdf_parts
        else:
            raise FileNotFoundError("No file uploaded")
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return None


# Session state initialization
session_vars = [
    "resume_evaluation", "percentage_match", "interview_questions",
    "skill_gap_analysis", "formatting_suggestions", "ats_compatibility"
]
for var in session_vars:
    if var not in st.session_state:
        st.session_state[var] = ""


# Custom CSS Styling
st.markdown("""
    <style>
        .main { background-color: #f0efe9; color: #5c5d5f; font-family: 'Arial', sans-serif; }
        .css-1d391kg { background-color: #5c5d5f; color: #5c5d5f; }
        .eczjsme8 h1,h3 { color: #decfbf; }
        .e1nzilvr5 h1,h3 { color: #decfbf; }
        .stButton button { background-color: #decfbf; color: #5c5d5f; border-radius: 8px; padding: 10px 15px; border: none; transition: background-color 0.3s ease; }
        .stButton button:hover { background-color: #b5a191; color: #000; }
        .stTextArea textarea { border: 1px solid #d9dadb; border-radius: 6px; background-color: #ffffff; color: #5c5d5f; }
        h1, h2, h3 { color: #5c5d5f; font-weight: 600; }
        hr { border: 1px solid #d9dadb; }
        .stAlert { color: #000; }
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background-color: #f0efe9; }
        ::-webkit-scrollbar-thumb { background-color: #decfbf; border-radius: 6px; }
        .block-container { padding: 2rem; }
        .css-1v3fvcr { color: #f0efe9; background-color: #000; }
        .e1nzilvr4 p { color: #5c5d5f; }
    </style>
""", unsafe_allow_html=True)


# Sidebar Content
st.sidebar.title("🧑‍💼 Talk TO CV")
st.sidebar.markdown("""
    - Analyze your resume against a job description using AI-powered tools:
    - Get feedback on your resume's strengths and weaknesses 
    - Check ATS compatibility
    - Receive interview questions and more!
""")

# App Main Header
st.title("📄 Talk TO CV")
st.markdown("""
Welcome to **Talk TO CV**! Upload your resume and get detailed insights on its alignment with your job description. 
Improve your chances of passing ATS systems and impressing hiring managers with tailored suggestions.
""")
st.markdown("---")

# User Input for Job Description and Resume Upload
st.subheader("Upload Your Resume and Job Description")
st.markdown("### 🔍 **Job Description**")
input_text = st.text_area("Enter your Job Description", key="input", height=200)
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    success_message = st.success("PDF Uploaded Successfully!", icon="✅")


# AI Prompt Definitions
prompts = {
    "resume_evaluation": "You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. Please share your professional evaluation on whether the candidate's profile aligns with the role. Highlight strengths and weaknesses of the applicant.",
    "percentage_match": "You are a skilled ATS scanner. Evaluate the resume and give a percentage match with the job description, missing keywords, and your thoughts.",
    "interview_questions": "Generate 10 interview questions based on the resume relevant to a web developer role.",
    "skill_gap_analysis": "Analyze the resume to identify skill gaps and suggest improvements to be a better fit for the role.",
    "formatting_suggestions": "Evaluate the resume's formatting and suggest improvements, including layout, font usage, and missing sections.",
    "ats_compatibility": "Review the resume for ATS compatibility and highlight potential parsing issues.",
    "role_suggestions": "Based on the resume, suggest job roles that match the candidate's skills and experience, explaining why each role is suitable."
}


# Sidebar Action Buttons
actions = [
    {"label": "📝 Review Resume", "key": "resume_evaluation"},
    {"label": "📊 Percentage Match", "key": "percentage_match"},
    {"label": "❓ Interview Questions", "key": "interview_questions"},
    {"label": "🔍 Skill Gap Analysis", "key": "skill_gap_analysis"},
    {"label": "💼 Formatting Suggestions", "key": "formatting_suggestions"},
    {"label": "⚙️ ATS Compatibility Check", "key": "ats_compatibility"},
    {"label": "🧑‍💼 Role Suggestions", "key": "role_suggestions"}
]

for action in actions:
    if st.sidebar.button(action["label"]):
        with st.spinner("Analyzing..."):
            pdf_content = input_pdf_setup(uploaded_file)
            if pdf_content:
                success_message.empty()
                response = get_gemini_response(input_text, pdf_content, prompts[action["key"]])
                st.session_state[action["key"]] = response
                st.success(f"✅ {action['label']} Complete!")
                st.markdown(f"### {action['label'].replace('⚙️ ', '').replace('💼 ', '')}")
                st.write(response)


# if st.sidebar.button("❓ Interview Questions"):
#     with st.spinner("Generating interview questions..."):
#         pdf_content = input_pdf_setup(uploaded_file)
#         if pdf_content:
#             success_message.empty()
#             if not input_text.strip():
#                 # No job description provided, fallback to web developer questions
#                 response = get_gemini_response(input_text, pdf_content, prompts["interview_questions"], role="web developer")
#             else:
#                 # Generate questions based on job description
#                 response = get_gemini_response(input_text, pdf_content, prompts["interview_questions"])

#             st.session_state["interview_questions"] = response
#             st.success("✅ Interview Questions Generated!")
#             st.markdown("### Interview Questions and Answers")
#             st.write(response)

st.markdown("---")

# Chat with Resume
st.subheader("Chat with Your Resume")
st.markdown("### 🗣️ **Ask Questions about your Resume**")
chat_input = st.text_area("Ask Anything", key="chat_input", height=100)

if st.button("Enter"):
    if chat_input and uploaded_file:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            chat_prompt = f"Based on the resume, {chat_input}"
            response = get_gemini_response(chat_input, pdf_content, chat_prompt)
            st.success("✅ Chat Response Ready!")
            st.markdown("### Chat Response")
            st.write(response)
        else:
            st.write("Ask a question about your resume.")


# Download Summary Report
if st.button("Download Summary Report"):
    summary_content = f"""
    ## ATS Resume Expert Summary Report

    ### Job Description:
    {input_text}

    ### Resume Evaluation:
    {st.session_state['resume_evaluation']}

    ### Percentage Match:
    {st.session_state['percentage_match']}

    ### Interview Questions:
    {st.session_state['interview_questions']}

    ### Skill Gap Analysis:
    {st.session_state['skill_gap_analysis']}

    ### Resume Formatting Suggestions:
    {st.session_state['formatting_suggestions']}

    ### ATS Compatibility Check:
    {st.session_state['ats_compatibility']}
    """
    summary_bytes = io.BytesIO(summary_content.encode("utf-8"))
    st.download_button("Download Summary as Text File", data=summary_bytes, file_name="resume_summary_report.txt", mime="text/plain")
