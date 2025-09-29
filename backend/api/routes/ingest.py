from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request, Form
from pydantic import BaseModel
from typing import List, Optional
import os
import aiofiles
from sqlalchemy.orm import Session

from core.database import get_db, Document, Chunk
from core.vector_store import VectorStore
from services.ingestion import IngestionService

router = APIRouter()

class IngestResponse(BaseModel):
    message: str
    document_id: str
    chunks_created: int

class IngestStatus(BaseModel):
    total_documents: int
    total_chunks: int
    total_vectors: int

@router.post("/upload", response_model=IngestResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a file and add it to our knowledge base"""
    try:
        vector_store: VectorStore = request.app.state.vector_store
        ingestion_service = IngestionService(db, vector_store)
        
        # Save the file somewhere temporarily
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process the file and add it to our brain
        document_id, chunks_created = await ingestion_service.ingest_file(
            file_path=file_path,
            title=title or file.filename,
            source="upload"
        )
        
        # Clean up the temp file
        os.remove(file_path)
        
        return IngestResponse(
            message=f"Successfully ingested {file.filename}",
            document_id=document_id,
            chunks_created=chunks_created
        )
        
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text", response_model=IngestResponse)
async def ingest_text(
    request: Request,
    title: str,
    content: str,
    source: str = "manual",
    db: Session = Depends(get_db)
):
    """Add some text directly without uploading a file"""
    try:
        vector_store: VectorStore = request.app.state.vector_store
        ingestion_service = IngestionService(db, vector_store)
        
        document_id, chunks_created = await ingestion_service.ingest_text(
            content=content,
            title=title,
            source=source
        )
        
        return IngestResponse(
            message=f"Successfully ingested text: {title}",
            document_id=document_id,
            chunks_created=chunks_created
        )
        
    except Exception as e:
        print(f"Text ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=IngestStatus)
async def get_ingest_status(request: Request, db: Session = Depends(get_db)):
    """Show me how much stuff we've got stored"""
    try:
        vector_store: VectorStore = request.app.state.vector_store
        
        total_documents = db.query(Document).count()
        total_chunks = db.query(Chunk).count()
        vector_stats = vector_store.get_stats()
        
        return IngestStatus(
            total_documents=total_documents,
            total_chunks=total_chunks,
            total_vectors=vector_stats['total_vectors']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    """Show me all the documents in our knowledge base"""
    try:
        documents = db.query(Document).all()
        return [
            {
                "id": doc.id,
                "title": doc.title,
                "source": doc.source,
                "path": doc.path,
                "created_at": doc.created_at.isoformat(),
                "chunk_count": len(doc.chunks)
            }
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Remove a document from our knowledge base (bye bye!)"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Remove from database (this also deletes all the related chunks)
        db.delete(document)
        db.commit()
        
        # TODO: In a real app, we'd rebuild the search index here
        # For now, we're just being lazy about it
        
        return {"message": f"Document {document.title} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
