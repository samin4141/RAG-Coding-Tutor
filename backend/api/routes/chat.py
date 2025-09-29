from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from sqlalchemy.orm import Session

from core.database import get_db, Document
from core.vector_store import VectorStore
from core.llm_client import LLMClient

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
        llm_client: LLMClient = req.app.state.llm_client
        
        # Retrieve relevant context
        search_results = vector_store.hybrid_search(
            request.query, 
            k=12, 
            k_final=5, 
            threshold=0.35
        )
        
        # Build context from search results
        context_parts = []
        sources = []
        
        for result in search_results:
            # Get document info
            doc = db.query(Document).filter(Document.id == result['document_id']).first()
            if doc:
                source_info = {
                    'title': doc.title,
                    'path': doc.path,
                    'section': result['metadata'].get('section', ''),
                    'score': result['score']
                }
                sources.append(source_info)
                
                # Format context with source attribution
                section = result['metadata'].get('section', '')
                source_label = f"[{doc.path}#{section}]" if section else f"[{doc.path}]"
                context_parts.append(f"{source_label}\n{result['text']}")
        
        context = "\n\n".join(context_parts)
        
        # Generate response
        if request.stream:
            def generate_stream():
                for chunk in llm_client.generate_stream(
                    llm_client.chat(request.query, context)
                ):
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                
                # Send sources at the end
                yield f"data: {json.dumps({'sources': sources, 'done': True})}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache"}
            )
        else:
            response = llm_client.chat(request.query, context)
            return ChatResponse(response=response, sources=sources)
            
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_models(req: Request):
    """List available LLM models"""
    try:
        llm_client: LLMClient = req.app.state.llm_client
        models = llm_client.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def chat_health(req: Request):
    """Check chat service health"""
    try:
        llm_client: LLMClient = req.app.state.llm_client
        vector_store: VectorStore = req.app.state.vector_store
        
        llm_connected = llm_client.check_connection()
        vector_stats = vector_store.get_stats()
        
        return {
            "llm_connected": llm_connected,
            "vector_store": vector_stats,
            "status": "healthy" if llm_connected else "llm_disconnected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
