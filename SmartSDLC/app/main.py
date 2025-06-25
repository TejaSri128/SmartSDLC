# File: app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import torch
import requests

from app.pdf_parser import extract_and_classify_requirements
from app.code_generator import generate_code
from app.bug_fixer import fix_code
from app.summarizer import summarize_code
from app.test_case_generator import generate_test_cases
from app.chatbot import chat_with_sdlc_bot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=4)

GROQ_API_KEY = "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"

def has_gpu():
    return torch.cuda.is_available()

async def run_blocking(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lambda: func(*args))

def query_grok_chatbot(prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.5
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Groq fallback error: {str(e)}"

@app.post("/upload-requirements")
async def upload_requirements(file: UploadFile = File(...)):
    try:
        content = await file.read()
        return await run_blocking(extract_and_classify_requirements, content)
    except Exception:
        content = await file.read()
        return query_grok_chatbot("Extract and classify these requirements:\n" + content.decode())

@app.post("/generate-code")
async def generate_code_from_prompt(data: dict):
    prompt = data.get("prompt", "")
    if not prompt:
        return {"error": "No prompt provided."}
    try:
        return await run_blocking(generate_code, prompt)
    except Exception:
        return query_grok_chatbot("Generate code for this prompt:\n" + prompt)

@app.post("/fix-bugs")
async def fix_bugs(data: dict):
    code = data.get("code", "")
    if not code:
        return {"error": "No code provided."}
    try:
        return await run_blocking(fix_code, code)
    except Exception:
        return query_grok_chatbot("Fix bugs in this code:\n" + code)

@app.post("/generate-tests")
async def generate_tests(data: dict):
    code = data.get("code", "")
    if not code:
        return {"error": "No code provided."}
    try:
        return await run_blocking(generate_test_cases, code)
    except Exception:
        return query_grok_chatbot("Generate test cases for this code:\n" + code)

@app.post("/summarize")
async def summarize(data: dict):
    code = data.get("code", "")
    if not code:
        return {"error": "No code provided."}
    try:
        return await run_blocking(summarize_code, code)
    except Exception:
        return query_grok_chatbot("Summarize this code:\n" + code)

@app.post("/chatbot")
async def chatbot(data: dict):
    query = data.get("query", "")
    if not query:
        return {"error": "No query provided."}

    try:
        if has_gpu():
            primary = await run_blocking(chat_with_sdlc_bot, query)
            if isinstance(primary, dict) and "text" in primary:
                return primary["text"]
            elif isinstance(primary, str):
                return primary
            else:
                raise Exception("Invalid HuggingFace output")
        else:
            raise Exception("GPU not available")
    except Exception:
        return query_grok_chatbot(query)
