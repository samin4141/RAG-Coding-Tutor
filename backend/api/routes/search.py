from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from core.database import get_db, Document
from core.vector_store import VectorStore

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    k: int = 10
    threshold: float = 0.35
    search_type: str = "hybrid"  # "vector", "keyword", or "hybrid"

class SearchResult(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any]
    document_title: str
    document_path: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_found: int
    query: str

@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Search through ingested documents"""
    try:
        vector_store: VectorStore = req.app.state.vector_store
        
        # Perform search based on type
        if request.search_type == "vector":
            results = vector_store.search(
                request.query, 
                k=request.k, 
                threshold=request.threshold
            )
        elif request.search_type == "keyword":
            results = vector_store._keyword_search(request.query, k=request.k)
        else:  # hybrid
            results = vector_store.hybrid_search(
                request.query,
                k=request.k,
                k_final=request.k,
                threshold=request.threshold
            )
        
        # Enrich results with document information
        search_results = []
        for result in results:
            document = db.query(Document).filter(
                Document.id == result['document_id']
            ).first()
            
            if document:
                search_result = SearchResult(
                    chunk_id=result['chunk_id'],
                    text=result['text'],
                    score=result['score'],
                    metadata=result['metadata'],
                    document_title=document.title,
                    document_path=document.path
                )
                search_results.append(search_result)
        
        return SearchResponse(
            results=search_results,
            total_found=len(search_results),
            query=request.query
        )
        
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{chunk_id}")
async def find_similar(
    chunk_id: str,
    k: int = 5,
    req: Request,
    db: Session = Depends(get_db)
):
    """Find chunks similar to a given chunk"""
    try:
        from core.database import Chunk
        
        # Get the chunk
        chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        # Search for similar chunks using the chunk's text
        vector_store: VectorStore = req.app.state.vector_store
        results = vector_store.search(chunk.text, k=k+1, threshold=0.2)
        
        # Filter out the original chunk
        similar_results = [r for r in results if r['chunk_id'] != chunk_id][:k]
        
        # Enrich with document info
        search_results = []
        for result in similar_results:
            document = db.query(Document).filter(
                Document.id == result['document_id']
            ).first()
            
            if document:
                search_result = SearchResult(
                    chunk_id=result['chunk_id'],
                    text=result['text'],
                    score=result['score'],
                    metadata=result['metadata'],
                    document_title=document.title,
                    document_path=document.path
                )
                search_results.append(search_result)
        
        return {
            "original_chunk_id": chunk_id,
            "similar_chunks": search_results,
            "total_found": len(search_results)
        }
        
    except Exception as e:
        print(f"Similar search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topics")
async def get_topics(db: Session = Depends(get_db)):
    """Get available topics/skills from problems and documents"""
    try:
        from core.database import Problem
        
        # Get skills from problems
        problems = db.query(Problem).all()
        skills = set()
        tags = set()
        
        for problem in problems:
            if problem.skills:
                skills.update(problem.skills)
            if problem.tags:
                tags.update(problem.tags)
        
        # Get document paths as topics
        documents = db.query(Document).all()
        document_topics = set()
        for doc in documents:
            # Extract topic from path (e.g., "algorithms/sorting" -> "sorting")
            path_parts = doc.path.split('/')
            if len(path_parts) > 1:
                document_topics.add(path_parts[-2])  # Parent directory
        
        return {
            "skills": sorted(list(skills)),
            "tags": sorted(list(tags)),
            "document_topics": sorted(list(document_topics))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_search_stats(req: Request, db: Session = Depends(get_db)):
    """Get search and vector store statistics"""
    try:
        vector_store: VectorStore = req.app.state.vector_store
        
        # Get vector store stats
        vector_stats = vector_store.get_stats()
        
        # Get database stats
        from core.database import Chunk
        total_documents = db.query(Document).count()
        total_chunks = db.query(Chunk).count()
        
        return {
            "vector_store": vector_stats,
            "database": {
                "total_documents": total_documents,
                "total_chunks": total_chunks
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
