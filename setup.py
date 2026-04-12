

#!/usr/bin/env python3
'''
Automated Setup Script for Career Intelligence Platform
Run: python setup.py
'''

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print(f"\\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\\n")

def run_command(cmd, error_msg="Command failed"):
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"✗ {error_msg}")
        return False

def main():
    print_header("Career Intelligence Platform - Setup")
    
    # 1. Create directories
    print("Creating directories...")
    directories = [
        "backend/app/models",
        "backend/app/schemas",
        "backend/app/services",
        "backend/app/routers",
        "backend/app/utils",
        "scrapers",
        "data/skills_dictionary",
        "data/course_catalog",
        "vector_store/chroma_db",
        "uploads/cvs",
        "uploads/jds",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Directories created")
    
    # 2. Create virtual environment
    print_header("Setting Up Virtual Environment")
    
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        run_command("python -m venv venv")
    
    # 3. Install dependencies
    print_header("Installing Dependencies")
    
    if sys.platform == "win32":
        pip_cmd = "venv\\\\Scripts\\\\pip"
        python_cmd = "venv\\\\Scripts\\\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    if os.path.exists('backend/requirements.txt'):
        print("Installing Python packages...")
        run_command(f"{pip_cmd} install -r backend/requirements.txt")
        print("✓ Dependencies installed")
    
    # 4. Download SpaCy model
    print_header("Downloading NLP Models")
    print("Downloading SpaCy model (this may take a while)...")
    run_command(f"{python_cmd} -m spacy download en_core_web_lg")
    print("✓ SpaCy model downloaded")
    
    # 5. Setup database
    print_header("Database Setup")
    print("Please ensure PostgreSQL is installed and running.")
    print("\\nTo create the database, run:")
    print("  createdb career_platform")
    print("  psql career_platform < database_schema.sql")
    
    # 6. Create .env file
    print_header("Environment Configuration")
    
    if not os.path.exists('.env'):
        print("Creating .env file...")
        env_content = '''DATABASE_URL=postgresql://career_user:password@localhost:5432/career_platform
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
CHROMA_DB_PATH=./vector_store/chroma_db
DEBUG=True
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
'''
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ .env file created")
        print("⚠ Please update .env with your actual API keys")
    
    # 7. Final instructions
    print_header("Setup Complete!")
    
    print('''
Next Steps:

1. Update .env with your credentials
2. Initialize database: cd backend && python init_db.py
3. Start backend: cd backend && uvicorn app.main:app --reload
4. Visit: http://localhost:8000/docs

For more information, see README.md
''')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\nSetup interrupted by user")
        sys.exit(1)
