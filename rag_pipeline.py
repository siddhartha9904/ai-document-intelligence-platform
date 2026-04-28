import os 
from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader
)
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key=os.getenv("GEMINI_API_KEY")


#loading docs
# Loader Map
loaders = {
    ".pdf": PyMuPDFLoader,
    ".txt": TextLoader,
    ".docx": Docx2txtLoader,
    ".csv": CSVLoader
}

# Load Single File
def load_file(load_path):
    ext = Path(load_path).suffix.lower()

    if ext not in loaders:
        return []

    loader_class = loaders[ext]

    if ext == ".txt":
        loader = loader_class(load_path, encoding="utf-8")
    else:
        loader = loader_class(load_path)

    return loader.load()

# Load All Files 
def load_all_documents(folder="data"):
    all_docs = []

    for file in Path(folder).iterdir():
        if file.is_file():
            docs = load_file(str(file))
            all_docs.extend(docs)

    return all_docs

all_docs=load_all_documents()

#text splitter (chunks)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
chunks = text_splitter.split_documents(all_docs)

#embeddings

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
#loading into vector database
db = FAISS.from_documents(chunks, embeddings)

#llm
llm=ChatGoogleGenerativeAI(model='gemini-2.5-flash',temperature=0.3,api_key=api_key)

def ask_rag(query):
    #retrieve top docs or chunks
    docs=db.similarity_search(query,k=3)

    #building context
    context="\n\n".join([doc.page_content for doc in docs])

    #sources
    sources=list(set([doc.metadata.get('source','unknown') for doc in docs]))
    
    #prompt
    prompt = f"""
    You are an AI assistant.

    Answer ONLY using the provided context.

    If answer is not found in context, say:
    I don't know based on the documents.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    #response
    response=llm.invoke(prompt)

    return {
        "answer":response.content,
        "sources":sources
    }