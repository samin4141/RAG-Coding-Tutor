#!/usr/bin/env python3
"""
Let's get this RAG tutor set up and ready to go!
This script will initialize everything you need to start learning.
"""

import os
import sys
import asyncio
import subprocess

def run_command(command, description):
    """Run a command and tell you if it worked or not"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_backend():
    """Get the backend ready to rock and roll"""
    print("\n📦 Setting up backend...")
    
    # Jump into the backend folder
    os.chdir("backend")
    
    # Install all the Python stuff we need
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Set up the database and fill it with some good stuff
    print("\n🗄️ Initializing database...")
    try:
        # Set up the database tables
        from core.database import init_db
        init_db()
        print("✅ Database initialized")
        
        # Add some practice problems to work with
        print("🌱 Creating seed problems...")
        from seed_data import create_seed_problems
        create_seed_problems()
        
        # Add some study notes to learn from
        print("📚 Creating seed notes...")
        import asyncio
        from seed_notes import create_seed_notes
        asyncio.run(create_seed_notes())
        
        print("✅ Seed data created successfully")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    
    # Go back to root directory
    os.chdir("..")
    return True

def setup_frontend():
    """Get the frontend looking pretty and working"""
    print("\n🎨 Setting up frontend...")
    
    # Jump into the frontend folder
    os.chdir("frontend")
    
    # Install all the JavaScript goodies
    if not run_command("npm install", "Installing Node.js dependencies"):
        os.chdir("..")
        return False
    
    # Go back to root directory
    os.chdir("..")
    return True

def check_prerequisites():
    """Make sure you have all the tools we need"""
    print("🔍 Checking prerequisites...")
    
    required_tools = [
        ("python", "Python 3.8+"),
        ("pip", "pip package manager"),
        ("node", "Node.js 16+"),
        ("npm", "npm package manager"),
        ("docker", "Docker (optional, for code execution)")
    ]
    
    missing_tools = []
    
    for tool, description in required_tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {description}: Found")
            else:
                missing_tools.append((tool, description))
        except FileNotFoundError:
            if tool == "docker":
                print(f"⚠️ {description}: Not found (optional - code execution will use subprocess)")
            else:
                missing_tools.append((tool, description))
    
    if missing_tools:
        print(f"\n❌ Missing required tools:")
        for tool, description in missing_tools:
            print(f"   - {description}")
        print("\nPlease install the missing tools and run setup again.")
        return False
    
    return True

def main():
    """Let's set this whole thing up!"""
    print("🚀 Coding Interview RAG Tutor Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Install and start Ollama (see instructions below)")
    print("2. Run 'python start.py' to start the application")
    print("3. Open http://localhost:3000 in your browser")
    
    print("\n" + "=" * 50)
    print("📖 Ollama Installation Instructions:")
    print("1. Visit https://ollama.ai and download Ollama")
    print("2. Install Ollama on your system")
    print("3. Run: ollama pull llama3.2:latest")
    print("4. Run: ollama serve (to start the Ollama server)")
    print("=" * 50)

if __name__ == "__main__":
    main()
