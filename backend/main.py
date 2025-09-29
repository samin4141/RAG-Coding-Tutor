from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import os
from dotenv import load_dotenv

from api.routes import chat, ingest, practice, search
from core.database import init_db
from core.vector_store import VectorStore
from core.llm_client import LLMClient

load_dotenv()

app = FastAPI(title="Coding Interview RAG Tutor", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    # Initialize database
    init_db()
    
    # Initialize vector store
    vector_store = VectorStore()
    app.state.vector_store = vector_store
    
    # Initialize LLM client
    llm_client = LLMClient()
    app.state.llm_client = llm_client
    
    print("🚀 Coding Interview RAG Tutor started successfully!")
    print("📚 Vector store initialized")
    print("🤖 LLM client ready")

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])
app.include_router(practice.router, prefix="/api/practice", tags=["practice"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

@app.get("/")
async def root():
    return {"message": "Coding Interview RAG Tutor API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
