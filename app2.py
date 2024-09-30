from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image
import fitz  # PyMuPDF
import google.generativeai as genai

# Configure Google Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get the Gemini response
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

# Function to convert PDF to image and setup input
def input_pdf_setup(uploaded_file):
    try:
        if uploaded_file is not None:
            pdf = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
            images = []
            for page_num in range(pdf.page_count):
                page = pdf.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes()))
                images.append(img)

            if len(images) == 0:
                st.error("No pages found in the uploaded PDF.")
                return None

            first_page = images[0]
            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format="JPEG")
            img_byte_arr = img_byte_arr.getvalue()

            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode(),  # encode to base64
                }
            ]
            return pdf_parts
        else:
            raise FileNotFoundError("No file uploaded")
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return None

# Initialize session state variables for storing responses
if "resume_evaluation" not in st.session_state:
    st.session_state.resume_evaluation = ""
if "percentage_match" not in st.session_state:
    st.session_state.percentage_match = ""
if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = ""
if "skill_gap_analysis" not in st.session_state:
    st.session_state.skill_gap_analysis = ""
if "formatting_suggestions" not in st.session_state:
    st.session_state.formatting_suggestions = ""
if "ats_compatibility" not in st.session_state:
    st.session_state.ats_compatibility = ""
if "chat_response" not in st.session_state:
    st.session_state.chat_response = ""

# Add styles for the app
st.markdown("""
    <style>
        /* Your CSS styles go here */
        .main { background-color: #f0efe9; color: #5c5d5f; font-family: 'Arial', sans-serif; }
        .stButton button { background-color: #decfbf; color: #5c5d5f; border-radius: 8px; padding: 10px 15px; border: none; }
        .stButton button:hover { background-color: #b5a191; color: #000; }
        /* Other styles... */
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🧑‍💼 Talk TO CV")
st.sidebar.markdown(
    """
    - Analyze your resume against a job description using AI-powered tools:
    - Get feedback on your resume's strengths and weaknesses 
    - Check ATS compatibility
    - Receive interview questions and more!
"""
)

# App Header
st.title("📄 Talk TO CV")
st.markdown(
    """
Welcome to **Talk TO CV**! Upload your resume and get detailed insights on its alignment with your job description. 
Improve your chances of passing ATS systems and impressing hiring managers with tailored suggestions.
"""
)
st.markdown("---")

# Collect Input from User
st.subheader("Upload Your Resume and Job Description")
st.markdown("### 🔍 **Job Description**")
input_text = st.text_area("Enter your Job Description", key="input", height=200)

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
if uploaded_file:
    st.success("PDF Uploaded Successfully!", icon="✅")

# Prompts for AI
input_prompt1 = "Your evaluation prompt here..."
input_prompt3 = "Your percentage match prompt here..."
input_prompt4 = "Your interview question prompt here..."
input_prompt5 = "Your skill gap analysis prompt here..."
input_prompt6 = "Your formatting suggestions prompt here..."
input_prompt7 = "Your ATS compatibility prompt here..."
input_prompt8 = "Your role suggestions prompt here..."

# Action Buttons
if st.sidebar.button("📝 Review Resume") or st.sidebar.button("📊 Percentage Match"):
    st.session_state.chat_response = ""  # Clear chat when any other action is pressed
    # Your code to handle these actions...

# Chat with Resume Section
st.subheader("Chat with Your Resume")
chat_input = st.text_area("Ask Anything", key="chat_input", height=100)

# Add an "Enter" button to trigger chat response
if st.button("Enter"):
    if chat_input and uploaded_file:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            chat_prompt = f"Based on the resume, {chat_input}"
            st.session_state.chat_response = get_gemini_response(chat_input, pdf_content, chat_prompt)
            st.success("✅ Chat Response Ready!")
            st.markdown("### Chat Response")
            st.write(st.session_state.chat_response)
else:
    if not st.session_state.chat_response:
        st.write("Ask a question about your resume.")

# Download Summary Report Button
if st.button("Download Summary Report"):
    summary_content = f"""
    ## ATS Resume Expert Summary Report

    ### Job Description:
    {input_text}

    ### Resume Evaluation:
    {st.session_state.resume_evaluation}

    ### Percentage Match:
    {st.session_state.percentage_match}

    ### Interview Questions:
    {st.session_state.interview_questions}

    ### Skill Gap Analysis:
    {st.session_state.skill_gap_analysis}

    ### Resume Formatting Suggestions:
    {st.session_state.formatting_suggestions}

    ### ATS Compatibility Check:
    {st.session_state.ats_compatibility}
    """
    summary_bytes = io.BytesIO(summary_content.encode("utf-8"))

    st.download_button(
        label="Download Summary as Text File",
        data=summary_bytes,
        file_name="resume_summary_report.txt",
        mime="text/plain",
    )
