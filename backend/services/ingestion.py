import os
import re
from typing import List, Dict, Any, Tuple
import markdown
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from core.database import Document, Chunk
from core.vector_store import VectorStore

class IngestionService:
    def __init__(self, db: Session, vector_store: VectorStore):
        self.db = db
        self.vector_store = vector_store
    
    async def ingest_file(self, file_path: str, title: str, source: str) -> Tuple[str, int]:
        """Ingest a file and return document_id and chunks_created"""
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine file type and process accordingly
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.md', '.markdown']:
            chunks = self._chunk_markdown(content, file_path)
        elif file_ext in ['.py', '.cpp', '.java', '.js', '.ts']:
            chunks = self._chunk_code(content, file_path, file_ext)
        elif file_ext in ['.txt']:
            chunks = self._chunk_text(content, file_path)
        else:
            # Default to text chunking
            chunks = self._chunk_text(content, file_path)
        
        return await self.ingest_text(content, title, source, chunks)
    
    async def ingest_text(self, content: str, title: str, source: str, chunks: List[Dict] = None) -> Tuple[str, int]:
        """Ingest text content directly"""
        
        # Create document
        document = Document(
            title=title,
            source=source,
            path=f"{source}/{title}"
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        # Create chunks if not provided
        if chunks is None:
            chunks = self._chunk_text(content, title)
        
        # Create chunk records
        chunk_records = []
        for i, chunk_data in enumerate(chunks):
            chunk = Chunk(
                document_id=document.id,
                chunk_idx=i,
                text=chunk_data['text'],
                metadata=chunk_data.get('metadata', {})
            )
            self.db.add(chunk)
            chunk_records.append(chunk)
        
        self.db.commit()
        
        # Prepare chunks for vector store
        vector_chunks = []
        for chunk in chunk_records:
            vector_chunks.append({
                'id': chunk.id,
                'text': chunk.text,
                'metadata': chunk.metadata
            })
        
        # Add to vector store
        self.vector_store.add_chunks(vector_chunks)
        
        return document.id, len(chunks)
    
    def _chunk_markdown(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Chunk markdown content by headings"""
        chunks = []
        
        # Convert markdown to HTML to parse structure
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Split by headings
        current_section = ""
        current_heading = ""
        current_text = []
        
        lines = content.split('\n')
        
        for line in lines:
            # Check if line is a heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if heading_match:
                # Save previous section if it has content
                if current_text:
                    text = '\n'.join(current_text).strip()
                    if text:
                        chunks.append({
                            'text': text,
                            'metadata': {
                                'section': current_heading,
                                'file_path': file_path,
                                'type': 'markdown'
                            }
                        })
                
                # Start new section
                current_heading = heading_match.group(2)
                current_text = [line]  # Include the heading
            else:
                current_text.append(line)
        
        # Add final section
        if current_text:
            text = '\n'.join(current_text).strip()
            if text:
                chunks.append({
                    'text': text,
                    'metadata': {
                        'section': current_heading,
                        'file_path': file_path,
                        'type': 'markdown'
                    }
                })
        
        # If no headings found, chunk by size
        if not chunks:
            chunks = self._chunk_by_size(content, file_path, chunk_size=1500, overlap=150)
        
        return chunks
    
    def _chunk_code(self, content: str, file_path: str, file_ext: str) -> List[Dict[str, Any]]:
        """Chunk code by functions/classes"""
        chunks = []
        
        if file_ext == '.py':
            chunks = self._chunk_python(content, file_path)
        else:
            # For other languages, use simple function-based chunking
            chunks = self._chunk_by_functions(content, file_path, file_ext)
        
        # If no functions found, chunk by size
        if not chunks:
            chunks = self._chunk_by_size(content, file_path, chunk_size=1000, overlap=100)
        
        return chunks
    
    def _chunk_python(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Chunk Python code by functions and classes"""
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_function = ""
        indent_level = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check for function or class definition
            if stripped.startswith('def ') or stripped.startswith('class '):
                # Save previous chunk
                if current_chunk:
                    text = '\n'.join(current_chunk).strip()
                    if text:
                        chunks.append({
                            'text': text,
                            'metadata': {
                                'function': current_function,
                                'file_path': file_path,
                                'type': 'python',
                                'line_start': i - len(current_chunk) + 1,
                                'line_end': i
                            }
                        })
                
                # Start new chunk
                current_function = stripped.split('(')[0].replace('def ', '').replace('class ', '')
                current_chunk = [line]
                indent_level = len(line) - len(line.lstrip())
            
            elif current_chunk:
                # Continue current chunk if indented or empty line
                line_indent = len(line) - len(line.lstrip()) if line.strip() else indent_level
                if line_indent > indent_level or not line.strip():
                    current_chunk.append(line)
                else:
                    # End of function/class
                    text = '\n'.join(current_chunk).strip()
                    if text:
                        chunks.append({
                            'text': text,
                            'metadata': {
                                'function': current_function,
                                'file_path': file_path,
                                'type': 'python',
                                'line_start': i - len(current_chunk),
                                'line_end': i - 1
                            }
                        })
                    current_chunk = [line]
                    current_function = ""
            else:
                current_chunk.append(line)
        
        # Add final chunk
        if current_chunk:
            text = '\n'.join(current_chunk).strip()
            if text:
                chunks.append({
                    'text': text,
                    'metadata': {
                        'function': current_function,
                        'file_path': file_path,
                        'type': 'python',
                        'line_start': len(lines) - len(current_chunk) + 1,
                        'line_end': len(lines)
                    }
                })
        
        return chunks
    
    def _chunk_by_functions(self, content: str, file_path: str, file_ext: str) -> List[Dict[str, Any]]:
        """Generic function-based chunking for various languages"""
        chunks = []
        lines = content.split('\n')
        
        # Simple patterns for different languages
        function_patterns = {
            '.cpp': r'^\s*(int|void|bool|string|auto)\s+\w+\s*\(',
            '.java': r'^\s*(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\(',
            '.js': r'^\s*(function\s+\w+|const\s+\w+\s*=|\w+\s*:\s*function)',
            '.ts': r'^\s*(function\s+\w+|const\s+\w+\s*=|\w+\s*:\s*function)'
        }
        
        pattern = function_patterns.get(file_ext, r'^\s*\w+.*\{')
        
        current_chunk = []
        brace_count = 0
        in_function = False
        
        for i, line in enumerate(lines):
            if re.match(pattern, line):
                # Save previous chunk
                if current_chunk and in_function:
                    text = '\n'.join(current_chunk).strip()
                    if text:
                        chunks.append({
                            'text': text,
                            'metadata': {
                                'file_path': file_path,
                                'type': file_ext[1:],  # Remove dot
                                'line_start': i - len(current_chunk) + 1,
                                'line_end': i
                            }
                        })
                
                current_chunk = [line]
                brace_count = line.count('{') - line.count('}')
                in_function = True
            
            elif in_function:
                current_chunk.append(line)
                brace_count += line.count('{') - line.count('}')
                
                if brace_count <= 0:
                    # End of function
                    text = '\n'.join(current_chunk).strip()
                    if text:
                        chunks.append({
                            'text': text,
                            'metadata': {
                                'file_path': file_path,
                                'type': file_ext[1:],
                                'line_start': i - len(current_chunk) + 1,
                                'line_end': i + 1
                            }
                        })
                    current_chunk = []
                    in_function = False
            else:
                current_chunk.append(line)
        
        return chunks
    
    def _chunk_text(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Chunk plain text by size"""
        return self._chunk_by_size(content, file_path, chunk_size=1500, overlap=150)
    
    def _chunk_by_size(self, content: str, file_path: str, chunk_size: int = 1500, overlap: int = 150) -> List[Dict[str, Any]]:
        """Chunk content by character size with overlap"""
        chunks = []
        
        if len(content) <= chunk_size:
            return [{
                'text': content,
                'metadata': {
                    'file_path': file_path,
                    'type': 'text',
                    'chunk_size': len(content)
                }
            }]
        
        start = 0
        chunk_idx = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # Try to break at sentence or paragraph boundary
            if end < len(content):
                # Look for sentence endings
                for i in range(end, max(start + chunk_size // 2, end - 200), -1):
                    if content[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk_text = content[start:end].strip()
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'file_path': file_path,
                        'type': 'text',
                        'chunk_idx': chunk_idx,
                        'chunk_size': len(chunk_text),
                        'start_pos': start,
                        'end_pos': end
                    }
                })
            
            start = end - overlap
            chunk_idx += 1
        
        return chunks
