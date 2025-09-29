#!/usr/bin/env python3
"""
Time to fire up the RAG tutor!
This script gets both the backend and frontend running so you can start learning.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True
    
    def start_service(self, command, name, cwd=None):
        """Fire up a service and keep track of it"""
        print(f"🚀 Starting {name}...")
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.processes.append((process, name))
            
            # Start a thread to show us what's happening
            output_thread = threading.Thread(
                target=self._handle_output,
                args=(process, name),
                daemon=True
            )
            output_thread.start()
            
            return process
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return None
    
    def _handle_output(self, process, name):
        """Show output from our running services"""
        while self.running and process.poll() is None:
            try:
                line = process.stdout.readline()
                if line:
                    print(f"[{name}] {line.strip()}")
            except:
                break
    
    def stop_all(self):
        """Shut down everything gracefully"""
        print("\n🛑 Stopping all services...")
        self.running = False
        
        for process, name in self.processes:
            if process.poll() is None:
                print(f"Stopping {name}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except:
                    pass
        
        print("✅ All services stopped")

def check_ollama():
    """Make sure Ollama is up and has the AI models we need"""
    print("🔍 Checking Ollama...")
    
    try:
        # See if Ollama is actually running
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print("⚠️ Ollama is not running. Please start Ollama first:")
            print("   1. Install Ollama from https://ollama.ai")
            print("   2. Run: ollama serve")
            print("   3. Run: ollama pull llama3.2:latest")
            return False
        
        # Make sure we have the right AI model installed
        import json
        try:
            data = json.loads(result.stdout)
            models = [model['name'] for model in data.get('models', [])]
            
            required_models = ['llama3.2:latest', 'llama3.2:3b', 'llama3.2']
            has_model = any(any(req in model for req in required_models) for model in models)
            
            if not has_model:
                print("⚠️ Required model not found. Please run:")
                print("   ollama pull llama3.2:latest")
                return False
            
            print("✅ Ollama is running with required models")
            return True
            
        except json.JSONDecodeError:
            print("⚠️ Could not parse Ollama response")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Ollama connection timeout")
        return False
    except FileNotFoundError:
        print("⚠️ curl not found. Please install curl or check Ollama manually")
        return True  # Continue anyway
    except Exception as e:
        print(f"⚠️ Error checking Ollama: {e}")
        return True  # Continue anyway

def check_ports():
    """Make sure the ports we need aren't already taken"""
    import socket
    
    ports = [
        (3000, "Frontend"),
        (8000, "Backend API")
    ]
    
    for port, service in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                print(f"⚠️ Port {port} ({service}) is already in use")
                sock.close()
                return False
        except:
            pass
        finally:
            sock.close()
    
    return True

def main():
    """Let's get this party started!"""
    print("🚀 Starting Coding Interview RAG Tutor")
    print("=" * 50)
    
    # Make sure setup was actually run first
    if not Path("backend/data").exists():
        print("❌ Backend not set up. Please run 'python setup.py' first.")
        sys.exit(1)
    
    if not Path("frontend/node_modules").exists():
        print("❌ Frontend not set up. Please run 'python setup.py' first.")
        sys.exit(1)
    
    # Double-check that Ollama is ready
    if not check_ollama():
        print("\n❌ Ollama check failed. The application may not work properly.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Make sure our ports are free
    if not check_ports():
        print("❌ Required ports are in use. Please stop other services and try again.")
        sys.exit(1)
    
    # Set up our service manager
    service_manager = ServiceManager()
    
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        service_manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Fire up the backend API
        backend_process = service_manager.start_service(
            "uvicorn main:app --host 0.0.0.0 --port 8000 --reload",
            "Backend",
            cwd="backend"
        )
        
        if not backend_process:
            print("❌ Failed to start backend")
            sys.exit(1)
        
        # Give the backend a moment to get ready
        print("⏳ Waiting for backend to start...")
        time.sleep(3)
        
        # Now start the frontend
        frontend_process = service_manager.start_service(
            "npm run dev",
            "Frontend",
            cwd="frontend"
        )
        
        if not frontend_process:
            print("❌ Failed to start frontend")
            service_manager.stop_all()
            sys.exit(1)
        
        # Give the frontend time to boot up
        print("⏳ Waiting for frontend to start...")
        time.sleep(5)
        
        print("\n🎉 All services started successfully!")
        print("=" * 50)
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("=" * 50)
        print("Press Ctrl+C to stop all services")
        
        # Keep everything running until user stops it
        while True:
            time.sleep(1)
            
            # Make sure both services are still alive
            if backend_process.poll() is not None:
                print("❌ Backend process died")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process died")
                break
    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        service_manager.stop_all()

if __name__ == "__main__":
    main()
