from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_message = Column(Text)
    bot_response = Column(Text)
    language_detected = Column(String)
    confidence_score = Column(Float)
    feedback = Column(Integer, default=0)  # -1=thumbs down, 0=no feedback, 1=thumbs up
    forwarded_to_admin = Column(Boolean, default=False)
    admin_response = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    title = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)
    chunk_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_text = Column(Text)
    chunk_index = Column(Integer)
    
    document = relationship("Document", back_populates="chunks")

class AdminOverride(Base):
    __tablename__ = "admin_overrides"
    
    id = Column(Integer, primary_key=True, index=True)
    question_pattern = Column(Text)
    override_response = Column(Text)
    language_code = Column(String)
    audio_file_path = Column(String, nullable=True)
    created_by = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)