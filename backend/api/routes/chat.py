from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from sqlalchemy.orm import Session

from core.database import get_db, Document
from core.vector_store import VectorStore
from core.llm_client import AIHelper

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    stream: bool = False

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request, db: Session = Depends(get_db)):
    """Chat endpoint with RAG"""
    try:
        vector_store: VectorStore = req.app.state.vector_store
        ai_helper: AIHelper = req.app.state.llm_client
        
        # Find relevant stuff from the user's notes
        search_results = vector_store.hybrid_search(
            request.query, 
            k=12, 
            k_final=5, 
            threshold=0.35
        )
        
        # Put together the context from what we found
        relevant_snippets = []
        source_references = []
        
        for result in search_results:
            # Get the document details
            doc = db.query(Document).filter(Document.id == result['document_id']).first()
            if doc:
                source_info = {
                    'title': doc.title,
                    'path': doc.path,
                    'section': result['metadata'].get('section', ''),
                    'score': result['score']
                }
                source_references.append(source_info)
                
                # Format the context with where it came from
                section = result['metadata'].get('section', '')
                source_label = f"[{doc.path}#{section}]" if section else f"[{doc.path}]"
                relevant_snippets.append(f"{source_label}\n{result['text']}")
        
        combined_context = "\n\n".join(relevant_snippets)
        
        # Get the AI's response
        if request.stream:
            def generate_stream():
                for chunk in ai_helper.ask_ai_streaming(
                    ai_helper.chat_with_context(request.query, combined_context)
                ):
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                
                # Send sources at the end
                yield f"data: {json.dumps({'sources': source_references, 'done': True})}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache"}
            )
        else:
            ai_response = ai_helper.chat_with_context(request.query, combined_context)
            return ChatResponse(response=ai_response, sources=source_references)
            
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_models(req: Request):
    """List available LLM models"""
    try:
        ai_helper: AIHelper = req.app.state.llm_client
        available_models = ai_helper.get_available_models()
        return {"models": available_models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def chat_health(req: Request):
    """Check chat service health"""
    try:
        ai_helper: AIHelper = req.app.state.llm_client
        vector_store: VectorStore = req.app.state.vector_store
        
        ai_is_working = ai_helper.is_ai_working()
        vector_stats = vector_store.get_stats()
        
        return {
            "llm_connected": ai_is_working,
            "vector_store": vector_stats,
            "status": "healthy" if ai_is_working else "llm_disconnected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
