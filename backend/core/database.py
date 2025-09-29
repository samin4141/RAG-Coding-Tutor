from sqlalchemy import create_engine, Column, String, Text, Integer, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
import uuid
from datetime import datetime
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/tutor.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_idx = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    metadata = Column(SQLiteJSON, default={})
    
    document = relationship("Document", back_populates="chunks")
    embedding = relationship("Embedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan")

class Embedding(Base):
    __tablename__ = "embeddings"
    
    chunk_id = Column(String, ForeignKey("chunks.id"), primary_key=True)
    vector_data = Column(Text, nullable=False)  # JSON serialized vector
    
    chunk = relationship("Chunk", back_populates="embedding")

class Problem(Base):
    __tablename__ = "problems"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    prompt_md = Column(Text, nullable=False)
    tags = Column(SQLiteJSON, default=[])
    skills = Column(SQLiteJSON, default=[])
    
    solutions = relationship("Solution", back_populates="problem", cascade="all, delete-orphan")
    testcases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="problem", cascade="all, delete-orphan")

class Solution(Base):
    __tablename__ = "solutions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    problem_id = Column(String, ForeignKey("problems.id"), nullable=False)
    lang = Column(String, nullable=False)
    code = Column(Text, nullable=False)
    explanation_md = Column(Text, default="")
    
    problem = relationship("Problem", back_populates="solutions")

class TestCase(Base):
    __tablename__ = "testcases"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    problem_id = Column(String, ForeignKey("problems.id"), nullable=False)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    visible = Column(Boolean, default=False)
    
    problem = relationship("Problem", back_populates="testcases")

class Attempt(Base):
    __tablename__ = "attempts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, default="default_user")  # For now, single user
    problem_id = Column(String, ForeignKey("problems.id"), nullable=False)
    lang = Column(String, nullable=False)
    code = Column(Text, nullable=False)
    passed = Column(Boolean, nullable=False)
    score = Column(Float, default=0.0)
    feedback_md = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    problem = relationship("Problem", back_populates="attempts")

def init_db():
    """Initialize database and create tables"""
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
