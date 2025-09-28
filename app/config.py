"""Configuration management with environment variables."""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./multimodal_content.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# S3 Storage
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY")
S3_SECRET = os.getenv("S3_SECRET")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Simple in-memory jobs store. Replace with Redis/DB later.
JOBS: Dict[str, Dict[str, Any]] = {}
