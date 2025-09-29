import docker
import tempfile
import os
import asyncio
import json
from typing import Dict, Any, Optional
import subprocess
import time

class CodeExecutor:
    def __init__(self):
        self.client = None
        self.timeout = 10  # give it 10 seconds max
        self.memory_limit = "256m"  # don't let it eat all our RAM
        
        # Let's see if Docker is available for safe code execution
        try:
            self.client = docker.from_env()
            # Quick ping to make sure Docker is actually working
            self.client.ping()
            print("✅ Docker client connected")
        except Exception as e:
            print(f"⚠️ Docker not available: {e}")
            print("No worries, we'll just run code directly (less safe but still works)")
    
    async def execute_code(
        self, 
        code: str, 
        language: str, 
        input_data: str = "", 
        expected_output: str = ""
    ) -> Dict[str, Any]:
        """Run some code and tell you what happened"""
        
        if language.lower() == "python":
            return await self._execute_python(code, input_data, expected_output)
        else:
            return {
                "passed": False,
                "output": "",
                "error": f"Language {language} not supported yet",
                "execution_time": 0
            }
    
    async def _execute_python(self, code: str, input_data: str, expected_output: str) -> Dict[str, Any]:
        """Time to run some Python code!"""
        
        if self.client:
            return await self._execute_python_docker(code, input_data, expected_output)
        else:
            return await self._execute_python_subprocess(code, input_data, expected_output)
    
    async def _execute_python_docker(self, code: str, input_data: str, expected_output: str) -> Dict[str, Any]:
        """Run Python code safely inside a Docker container"""
        
        try:
            # Make a temp folder for our code files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save the code to a file
                code_file = os.path.join(temp_dir, "solution.py")
                with open(code_file, 'w') as f:
                    f.write(code)
                
                # Save the input data too
                input_file = os.path.join(temp_dir, "input.txt")
                with open(input_file, 'w') as f:
                    f.write(input_data)
                
                # Fire up the Docker container!
                start_time = time.time()
                
                try:
                    result = self.client.containers.run(
                        "python:3.11-slim",
                        command=f"sh -c 'cd /code && python solution.py < input.txt'",
                        volumes={temp_dir: {'bind': '/code', 'mode': 'ro'}},
                        mem_limit=self.memory_limit,
                        timeout=self.timeout,
                        remove=True,
                        capture_output=True,
                        text=True
                    )
                    
                    execution_time = time.time() - start_time
                    output = result.decode('utf-8').strip()
                    error = None
                    
                except docker.errors.ContainerError as e:
                    execution_time = time.time() - start_time
                    output = e.stdout.decode('utf-8').strip() if e.stdout else ""
                    error = e.stderr.decode('utf-8').strip() if e.stderr else str(e)
                
                except Exception as e:
                    execution_time = time.time() - start_time
                    output = ""
                    error = str(e)
                
                # Check if output matches expected
                passed = self._compare_outputs(output, expected_output)
                
                return {
                    "passed": passed,
                    "output": output,
                    "error": error,
                    "execution_time": execution_time,
                    "expected_output": expected_output
                }
                
        except Exception as e:
            return {
                "passed": False,
                "output": "",
                "error": f"Docker execution error: {str(e)}",
                "execution_time": 0
            }
    
    async def _execute_python_subprocess(self, code: str, input_data: str, expected_output: str) -> Dict[str, Any]:
        """Run Python code directly on the system (backup plan)"""
        
        try:
            # Make a temp file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                code_file = f.name
            
            try:
                start_time = time.time()
                
                # Execute the code!
                process = subprocess.Popen(
                    ['python', code_file],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout
                )
                
                stdout, stderr = process.communicate(input=input_data)
                execution_time = time.time() - start_time
                
                output = stdout.strip()
                error = stderr.strip() if stderr else None
                
                # Check if output matches expected
                passed = self._compare_outputs(output, expected_output)
                
                return {
                    "passed": passed,
                    "output": output,
                    "error": error,
                    "execution_time": execution_time,
                    "expected_output": expected_output
                }
                
            finally:
                # Clean up our mess
                os.unlink(code_file)
                
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "output": "",
                "error": f"Code execution timed out after {self.timeout} seconds",
                "execution_time": self.timeout
            }
        except Exception as e:
            return {
                "passed": False,
                "output": "",
                "error": f"Execution error: {str(e)}",
                "execution_time": 0
            }
    
    def _compare_outputs(self, actual: str, expected: str) -> bool:
        """Check if what we got matches what we wanted"""
        
        # Clean up spacing and newlines
        actual_normalized = ' '.join(actual.split())
        expected_normalized = ' '.join(expected.split())
        
        # Try the simple approach first
        if actual_normalized == expected_normalized:
            return True
        
        # Maybe they're numbers? Let's check
        try:
            actual_num = float(actual_normalized)
            expected_num = float(expected_normalized)
            return abs(actual_num - expected_num) < 1e-9
        except ValueError:
            pass
        
        # Could be JSON data, let's see
        try:
            actual_json = json.loads(actual)
            expected_json = json.loads(expected)
            return actual_json == expected_json
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Last resort: compare line by line
        actual_lines = [line.strip() for line in actual.split('\n') if line.strip()]
        expected_lines = [line.strip() for line in expected.split('\n') if line.strip()]
        
        return actual_lines == expected_lines
    
    def get_supported_languages(self) -> list:
        """What languages can we actually run?"""
        return ["python"]  # Just Python for now, but we could add more!
    
    def is_docker_available(self) -> bool:
        """Is Docker actually working on this machine?"""
        return self.client is not None
