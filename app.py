from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import ask_rag
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
import shutil
import os

app=FastAPI(title="Multi-document RAG API",
            description="FastAPI backend for your gemini+FAISS RAG project",
            version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query:str

@app.get('/')
def home():
    return {"message":"Welcome to Multi-document RAG application"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask_question(request:QueryRequest):
    try:
        result=ask_rag(request.query)
        return result
    except Exception as e:
        return {"error":str(e)}

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):

    os.makedirs("data", exist_ok=True)

    file_path = f"data/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": f"{file.filename} uploaded successfully"
    }