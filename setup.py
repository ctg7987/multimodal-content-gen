#!/usr/bin/env python3
"""Setup script for Multimodal Content Generator."""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_python_dependencies():
    """Install Python dependencies."""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def install_node_dependencies():
    """Install Node.js dependencies."""
    web_dir = Path("web")
    if web_dir.exists():
        return run_command("cd web && npm install", "Installing Node.js dependencies")
    else:
        print("⚠️  Web directory not found, skipping Node.js setup")
        return True

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = """# API Keys (replace with your actual keys)
OPENAI_API_KEY=sk-your-openai-key-here
REPLICATE_API_TOKEN=r8_your-replicate-token-here

# Database
DATABASE_URL=sqlite:///./multimodal_content.db
REDIS_URL=redis://localhost:6379

# S3 Storage (optional)
S3_BUCKET=your_s3_bucket_name
S3_KEY=your_s3_access_key
S3_SECRET=your_s3_secret_key
S3_REGION=us-east-1

# Vector Database (optional)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment

# Application Settings
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
"""
        env_file.write_text(env_content)
        print("✅ .env file created")
        print("⚠️  Please update the API keys in .env file")
    else:
        print("✅ .env file already exists")

def create_database():
    """Create database tables."""
    print("🗄️  Creating database tables...")
    try:
        from app.db import create_tables
        create_tables()
        print("✅ Database tables created")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_imports():
    """Test if all imports work."""
    print("🧪 Testing imports...")
    try:
        from app.main import app
        from app.pipelines import text, image, rag, score, promptify
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Multimodal Content Generator")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_python_dependencies():
        print("❌ Python dependency installation failed")
        sys.exit(1)
    
    if not install_node_dependencies():
        print("❌ Node.js dependency installation failed")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Import test failed")
        sys.exit(1)
    
    # Create database
    if not create_database():
        print("❌ Database setup failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update API keys in .env file")
    print("2. Start the backend: uvicorn app.main:app --reload")
    print("3. Start the frontend: cd web && npm run dev")
    print("4. Run tests: python test_api.py")
    print("\n🌐 Access the application at http://localhost:3000")

if __name__ == "__main__":
    main()
