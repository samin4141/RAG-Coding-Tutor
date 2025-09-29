import requests
import json
from typing import Dict, Any, Iterator, Optional
import os

class LLMClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.2:latest"  # This is our go-to model, works pretty well
        
    def generate(self, prompt: str, model: Optional[str] = None, stream: bool = False, **kwargs) -> str:
        """Ask the AI to generate some text - pretty straightforward stuff"""
        model = model or self.model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=stream,
                timeout=60
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                result = response.json()
                return result.get("response", "")
                
        except requests.exceptions.RequestException as e:
            print(f"Uh oh, Ollama isn't happy: {e}")
            return "Hmm, looks like I can't reach the AI brain right now. Is Ollama actually running?"
    
    def generate_stream(self, prompt: str, model: Optional[str] = None, **kwargs) -> Iterator[str]:
        """Same as generate but streams the response as it comes - fancy!"""
        model = model or self.model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            yield data['response']
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            print(f"Stream broke, whoops: {e}")
            yield "Looks like the AI stream got disconnected. Double-check that Ollama is still running!"
    
    def _handle_stream_response(self, response) -> str:
        """Takes all the streaming chunks and glues them back together"""
        complete_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if 'response' in data:
                        complete_response += data['response']
                    if data.get('done', False):
                        break
                except json.JSONDecodeError:
                    continue  # Sometimes we get weird data, just skip it
        return complete_response
    
    def chat(self, query: str, context: str = "", system_prompt: str = None) -> str:
        """This is where the magic happens - chat with your own notes as context"""
        if system_prompt is None:
            system_prompt = """You are a coding interview tutor. Use only the provided context from the student's own notes and solutions. 

If the information is not in the context, say so clearly and suggest they might want to add more notes or practice problems on that topic.

Return short, precise explanations with code examples when useful. Always cite your sources by mentioning the file or section name."""
        
        if context:
            prompt = f"""System: {system_prompt}

Context from your notes:
{context}

Question: {query}

Answer:"""
        else:
            prompt = f"""System: {system_prompt}

Question: {query}

Answer: I don't have any relevant notes or context for this question. You might want to add some study materials or practice problems on this topic first."""
        
        return self.generate(prompt)
    
    def generate_feedback(self, student_code: str, canonical_code: str, problem_title: str, test_results: Dict[str, Any]) -> str:
        """Be a helpful coding tutor - compare student's attempt with the ideal solution"""
        system_prompt = """You are a coding interview tutor providing feedback on a student's solution.

Compare the student's code to the canonical solution and provide specific feedback on:
1. Correctness (did it pass the tests?)
2. Algorithm approach and efficiency
3. Code style and clarity
4. Edge case handling

Be constructive and specific. Cite line numbers when possible."""
        
        prompt = f"""System: {system_prompt}

Problem: {problem_title}

Student's Code:
```python
{student_code}
```

Canonical Solution:
```python
{canonical_code}
```

Test Results:
- Passed: {test_results.get('passed', 0)}/{test_results.get('total', 0)} tests
- Status: {'✅ All tests passed' if test_results.get('all_passed', False) else '❌ Some tests failed'}

Provide detailed feedback:"""
        
        return self.generate(prompt)
    
    def generate_hint(self, problem_prompt: str, context: str, hint_level: int = 1) -> str:
        """Give hints that get progressively more obvious - like a good friend helping you out"""
        hint_prompts = {
            1: "Give a very subtle hint about the approach without revealing the solution.",
            2: "Provide a more specific hint about the data structure or algorithm to use.",
            3: "Give a detailed hint with pseudocode but not the full implementation."
        }
        
        system_prompt = f"""You are a coding interview tutor providing hints. {hint_prompts.get(hint_level, hint_prompts[1])}

Use the provided context from the student's notes if relevant."""
        
        prompt = f"""System: {system_prompt}

Problem:
{problem_prompt}

Context from notes:
{context}

Hint (level {hint_level}):"""
        
        return self.generate(prompt)
    
    def check_connection(self) -> bool:
        """Quick health check - is our AI buddy actually awake?"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> list:
        """See what AI models you've got installed locally"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []
