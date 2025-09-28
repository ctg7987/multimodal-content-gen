"""Database models and connection."""
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .config import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Job(Base):
    """Job model for storing generation tasks."""
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, index=True)
    status = Column(String, default="processing")
    progress = Column(Integer, default=0)
    input_data = Column(JSON)
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(Text)


class BrandProfile(Base):
    """Brand profile model for storing brand information."""
    __tablename__ = "brand_profiles"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    voice = Column(Text)
    target_audience = Column(Text)
    key_messages = Column(JSON)
    tone = Column(String)
    values = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
