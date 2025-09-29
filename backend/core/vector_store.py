import faiss
import numpy as np
import json
import os
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from core.database import get_db, Chunk, Embedding
import pickle

class VectorStore:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5", vector_dim: int = 384):
        self.model_name = model_name
        self.vector_dim = vector_dim
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
        
        # Initialize sentence transformer
        print(f"Loading embedding model: {model_name}")
        self.encoder = SentenceTransformer(model_name)
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(vector_dim)  # Inner product for cosine similarity
        self.chunk_ids = []  # Keep track of chunk IDs corresponding to vectors
        
        # Load existing index if available
        self._load_index()
        
    def _load_index(self):
        """Load existing FAISS index and chunk IDs"""
        os.makedirs(self.vector_store_path, exist_ok=True)
        index_path = os.path.join(self.vector_store_path, "faiss.index")
        ids_path = os.path.join(self.vector_store_path, "chunk_ids.pkl")
        
        if os.path.exists(index_path) and os.path.exists(ids_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(ids_path, 'rb') as f:
                    self.chunk_ids = pickle.load(f)
                print(f"✅ Loaded existing vector index with {len(self.chunk_ids)} vectors")
            except Exception as e:
                print(f"⚠️ Error loading index: {e}. Starting fresh.")
                self.index = faiss.IndexFlatIP(self.vector_dim)
                self.chunk_ids = []
    
    def _save_index(self):
        """Save FAISS index and chunk IDs"""
        os.makedirs(self.vector_store_path, exist_ok=True)
        index_path = os.path.join(self.vector_store_path, "faiss.index")
        ids_path = os.path.join(self.vector_store_path, "chunk_ids.pkl")
        
        faiss.write_index(self.index, index_path)
        with open(ids_path, 'wb') as f:
            pickle.dump(self.chunk_ids, f)
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        embedding = self.encoder.encode([text], normalize_embeddings=True)
        return embedding[0]
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        embeddings = self.encoder.encode(texts, normalize_embeddings=True)
        return embeddings
    
    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Add chunks to vector store"""
        if not chunks:
            return
            
        texts = [chunk['text'] for chunk in chunks]
        chunk_ids = [chunk['id'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embed_texts(texts)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        self.chunk_ids.extend(chunk_ids)
        
        # Save embeddings to database
        db = next(get_db())
        try:
            for chunk_id, embedding in zip(chunk_ids, embeddings):
                # Check if embedding already exists
                existing = db.query(Embedding).filter(Embedding.chunk_id == chunk_id).first()
                if not existing:
                    db_embedding = Embedding(
                        chunk_id=chunk_id,
                        vector_data=json.dumps(embedding.tolist())
                    )
                    db.add(db_embedding)
            db.commit()
        finally:
            db.close()
        
        # Save index
        self._save_index()
        print(f"✅ Added {len(chunks)} chunks to vector store")
    
    def search(self, query: str, k: int = 12, threshold: float = 0.35) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embed_text(query)
        
        # Search FAISS index
        scores, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'), 
            min(k, self.index.ntotal)
        )
        
        # Get results above threshold
        results = []
        db = next(get_db())
        try:
            for score, idx in zip(scores[0], indices[0]):
                if score >= threshold and idx < len(self.chunk_ids):
                    chunk_id = self.chunk_ids[idx]
                    chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
                    if chunk:
                        results.append({
                            'chunk_id': chunk_id,
                            'text': chunk.text,
                            'score': float(score),
                            'metadata': chunk.metadata,
                            'document_id': chunk.document_id
                        })
        finally:
            db.close()
        
        return results
    
    def hybrid_search(self, query: str, k: int = 12, k_final: int = 5, threshold: float = 0.35) -> List[Dict[str, Any]]:
        """Hybrid search combining vector and keyword search"""
        # Vector search
        vector_results = self.search(query, k=k, threshold=threshold)
        
        # Simple keyword search (can be enhanced with BM25)
        keyword_results = self._keyword_search(query, k=k)
        
        # Combine and rerank
        combined_results = self._rerank_fusion(vector_results, keyword_results)
        
        return combined_results[:k_final]
    
    def _keyword_search(self, query: str, k: int = 20) -> List[Dict[str, Any]]:
        """Simple keyword search in chunk text"""
        query_terms = query.lower().split()
        results = []
        
        db = next(get_db())
        try:
            chunks = db.query(Chunk).all()
            for chunk in chunks:
                text_lower = chunk.text.lower()
                score = sum(1 for term in query_terms if term in text_lower)
                if score > 0:
                    results.append({
                        'chunk_id': chunk.id,
                        'text': chunk.text,
                        'score': score / len(query_terms),  # Normalize
                        'metadata': chunk.metadata,
                        'document_id': chunk.document_id
                    })
        finally:
            db.close()
        
        # Sort by score and return top k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:k]
    
    def _rerank_fusion(self, vector_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """Simple rank fusion of vector and keyword results"""
        # Create a combined score based on ranks
        chunk_scores = {}
        
        # Add vector search ranks
        for i, result in enumerate(vector_results):
            chunk_id = result['chunk_id']
            chunk_scores[chunk_id] = {
                'data': result,
                'vector_rank': i + 1,
                'keyword_rank': len(keyword_results) + 1,  # Default low rank
                'vector_score': result['score']
            }
        
        # Add keyword search ranks
        for i, result in enumerate(keyword_results):
            chunk_id = result['chunk_id']
            if chunk_id in chunk_scores:
                chunk_scores[chunk_id]['keyword_rank'] = i + 1
            else:
                chunk_scores[chunk_id] = {
                    'data': result,
                    'vector_rank': len(vector_results) + 1,
                    'keyword_rank': i + 1,
                    'vector_score': 0.0
                }
        
        # Calculate combined score (lower is better for ranks)
        for chunk_id in chunk_scores:
            data = chunk_scores[chunk_id]
            # Reciprocal rank fusion
            combined_score = (1.0 / data['vector_rank']) + (1.0 / data['keyword_rank'])
            data['combined_score'] = combined_score
        
        # Sort by combined score
        sorted_results = sorted(
            chunk_scores.values(), 
            key=lambda x: x['combined_score'], 
            reverse=True
        )
        
        return [item['data'] for item in sorted_results]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'total_vectors': self.index.ntotal,
            'vector_dimension': self.vector_dim,
            'model_name': self.model_name
        }
