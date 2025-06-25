import streamlit as st
import requests
import json
from streamlit_lottie import st_lottie as str

st.set_page_config(page_title="SmartSDLC - AI Assistant", layout="wide")

# Custom CSS styling
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }
    .stTextInput > div > div > input, .stTextArea textarea {
        background-color: black;
        border-radius: 0.5rem;
        border: 1px solid #dfe3e8;
        padding: 0.75rem;
    }
    .stButton button {
        background-color: #0066cc;
        color: white;
        border-radius: 0.5rem;
        font-weight: bold;
        padding: 0.75rem 1.5rem;
    }
    .stButton button:hover {
        background-color: #004a99;
    }
    .custom-box {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

API_BASE = "http://localhost:8000"

def call_api(endpoint, data=None, file=None):
    try:
        if file:
            files = {"file": file}
            res = requests.post(f"{API_BASE}/{endpoint}", files=files)
        else:
            headers = {"Content-Type": "application/json"}
            res = requests.post(f"{API_BASE}/{endpoint}", headers=headers, data=json.dumps(data))
        return res.json()
    except Exception as e:
        return {"error": str(e)}

st.title("🚀 SmartSDLC: AI-Enhanced Software Development Lifecycle")
st.subheader("An intelligent platform to streamline your SDLC using IBM Watsonx Generative AI")

st.sidebar.title("🧭 SmartSDLC Tools")
option = st.sidebar.radio("Select a feature:", [
    "📄 Requirement Upload and Classification",
    "🧠 AI Code Generator",
    "🛠️ Bug Fixer",
    "🧪 Test Case Generator",
    "📝 Code Summarizer",
    "💬 AI Chatbot Assistant"
])

if option == "📄 Requirement Upload and Classification":
    st.header("📄 Upload & Classify Requirements (PDF)")
    uploaded_file = st.file_uploader("Upload your PDF containing requirements", type="pdf")
    if uploaded_file and st.button("🔍 Classify Requirements"):
        results = call_api("upload-requirements", file=uploaded_file)
        st.subheader("📌 Classified SDLC Phases")
        if isinstance(results, list):
            for item in results:
                if isinstance(item, dict) and 'sentence' in item and 'phase' in item:
                    st.markdown(
                        f"""
                        <div class="custom-box">
                            <b>{item['sentence'].strip()}</b><br>
                            <span style='color: green; font-weight: bold;'>Phase: {item['phase'].strip()}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.error("Error: Unexpected response from API.")

elif option == "🧠 AI Code Generator":
    st.header("🧠 Generate Code from Description")
    prompt = st.text_area("📝 Enter your requirement/feature description:", height=150)
    if st.button("🚀 Generate Code"):
        result = call_api("generate-code", {"prompt": prompt})
        st.code(result, language='python')

elif option == "🛠️ Bug Fixer":
    st.header("🛠️ Fix Your Buggy Code")
    buggy_code = st.text_area("🐛 Paste buggy code here:", height=200)
    if st.button("🔧 Fix Code"):
        result = call_api("fix-bugs", {"code": buggy_code})
        st.code(result, language='python')

elif option == "🧪 Test Case Generator":
    st.header("🧪 Generate Test Cases")
    function_code = st.text_area("📜 Paste function or code block:", height=200)
    if st.button("🧬 Generate Tests"):
        result = call_api("generate-tests", {"code": function_code})
        st.code(result, language='python')

elif option == "📝 Code Summarizer":
    st.header("📝 Summarize Your Code")
    code_input = st.text_area("📥 Paste your code snippet for summary:", height=200)
    if st.button("📚 Summarize Code"):
        result = call_api("summarize", {"code": code_input})
        st.success(result)

elif option == "💬 AI Chatbot Assistant":
    st.header("💬 Ask the SmartSDLC Assistant")
    question = st.text_input("❓ Ask anything about SDLC")
    if st.button("🤖 Get Answer"):
        result = call_api("chatbot", {"query": question})
        st.success(result)
