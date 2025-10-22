#!/usr/bin/env python3
"""
Setup script for AI Knowledge Vault
This script helps with installation and initial configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages."""
    print("\n📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your Azure OpenAI credentials")
        return True
    else:
        print("❌ env_example.txt not found")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ["chroma_db", "uploads", "exports"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_azure_config():
    """Check if Azure OpenAI configuration is complete."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
    ]
    
    missing_vars = []
    with open(env_file, 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=your_" in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or incomplete configuration for: {', '.join(missing_vars)}")
        print("Please edit .env file with your Azure OpenAI credentials")
        return False
    
    print("✅ Azure OpenAI configuration looks complete")
    return True

def run_tests():
    """Run basic tests to verify installation."""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        import streamlit
        import langchain
        import chromadb
        import openai
        print("✅ All required packages imported successfully")
        
        # Test configuration loading
        from config import AZURE_OPENAI_API_KEY
        if AZURE_OPENAI_API_KEY and AZURE_OPENAI_API_KEY != "your_azure_openai_api_key_here":
            print("✅ Configuration loaded successfully")
        else:
            print("⚠️  Configuration not properly set")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Main setup function."""
    print("🧠 AI Knowledge Vault Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Check Azure configuration
    azure_configured = check_azure_config()
    
    # Run tests
    tests_passed = run_tests()
    
    print("\n" + "=" * 40)
    print("🎉 Setup Complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your Azure OpenAI credentials")
    print("2. Run: streamlit run main.py")
    print("3. Open http://localhost:8501 in your browser")
    
    if not azure_configured:
        print("\n⚠️  Remember to configure your Azure OpenAI credentials in .env file")
    
    if not tests_passed:
        print("\n⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
