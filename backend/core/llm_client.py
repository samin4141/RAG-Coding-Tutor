import requests
import json
from typing import Dict, Any, Iterator, Optional
import os

class AIHelper:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.default_model = "llama3.2:latest"  # This is our go-to model, works pretty well
        
    def ask_ai(self, question: str, model_name: Optional[str] = None, stream_response: bool = False, **extra_options) -> str:
        """Ask the AI to generate some text - pretty straightforward stuff"""
        model_to_use = model_name or self.default_model
        
        request_data = {
            "model": model_to_use,
            "prompt": question,
            "stream": stream_response,
            **extra_options
        }
        
        try:
            ai_response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=request_data,
                stream=stream_response,
                timeout=60
            )
            ai_response.raise_for_status()
            
            if stream_response:
                return self._collect_streaming_response(ai_response)
            else:
                response_data = ai_response.json()
                return response_data.get("response", "")
                
        except requests.exceptions.RequestException as e:
            print(f"Uh oh, Ollama isn't happy: {e}")
            return "Hmm, looks like I can't reach the AI brain right now. Is Ollama actually running?"
    
    def ask_ai_streaming(self, question: str, model_name: Optional[str] = None, **extra_options) -> Iterator[str]:
        """Same as ask_ai but streams the response as it comes - fancy!"""
        model_to_use = model_name or self.default_model
        
        request_data = {
            "model": model_to_use,
            "prompt": question,
            "stream": True,
            **extra_options
        }
        
        try:
            ai_response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=request_data,
                stream=True,
                timeout=60
            )
            ai_response.raise_for_status()
            
            for line in ai_response.iter_lines():
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
    
    def _collect_streaming_response(self, ai_response) -> str:
        """Takes all the streaming chunks and glues them back together"""
        full_answer = ""
        for line in ai_response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if 'response' in data:
                        full_answer += data['response']
                    if data.get('done', False):
                        break
                except json.JSONDecodeError:
                    continue  # Sometimes we get weird data, just skip it
        return full_answer
    
    def chat_with_context(self, user_question: str, relevant_notes: str = "", instructions: str = None) -> str:
        """This is where the magic happens - chat with your own notes as context"""
        if instructions is None:
            instructions = """You are a coding interview tutor. Use only the provided context from the student's own notes and solutions. 

If the information is not in the context, say so clearly and suggest they might want to add more notes or practice problems on that topic.

Return short, precise explanations with code examples when useful. Always cite your sources by mentioning the file or section name."""
        
        if relevant_notes:
            full_prompt = f"""System: {instructions}

Context from your notes:
{relevant_notes}

Question: {user_question}

Answer:"""
        else:
            full_prompt = f"""System: {instructions}

Question: {user_question}

Answer: I don't have any relevant notes or context for this question. You might want to add some study materials or practice problems on this topic first."""
        
        return self.ask_ai(full_prompt)
    
    def give_coding_feedback(self, student_solution: str, reference_solution: str, problem_name: str, test_results: Dict[str, Any]) -> str:
        """Be a helpful coding tutor - compare student's attempt with the ideal solution"""
        tutor_instructions = """You are a coding interview tutor providing feedback on a student's solution.

Compare the student's code to the canonical solution and provide specific feedback on:
1. Correctness (did it pass the tests?)
2. Algorithm approach and efficiency
3. Code style and clarity
4. Edge case handling

Be constructive and specific. Cite line numbers when possible."""
        
        feedback_prompt = f"""System: {tutor_instructions}

Problem: {problem_name}

Student's Code:
```python
{student_solution}
```

Canonical Solution:
```python
{reference_solution}
```

Test Results:
- Passed: {test_results.get('passed', 0)}/{test_results.get('total', 0)} tests
- Status: {'✅ All tests passed' if test_results.get('all_passed', False) else '❌ Some tests failed'}

Provide detailed feedback:"""
        
        return self.ask_ai(feedback_prompt)
    
    def give_hint(self, problem_description: str, student_notes: str, hint_level: int = 1) -> str:
        """Give hints that get progressively more obvious - like a good friend helping you out"""
        hint_prompts = {
            1: "Give a very subtle hint about the approach without revealing the solution.",
            2: "Provide a more specific hint about the data structure or algorithm to use.",
            3: "Give a detailed hint with pseudocode but not the full implementation."
        }
        
        hint_instructions = f"""You are a coding interview tutor providing hints. {hint_prompts.get(hint_level, hint_prompts[1])}

Use the provided context from the student's notes if relevant."""
        
        hint_prompt = f"""System: {hint_instructions}

Problem:
{problem_description}

Context from notes:
{student_notes}

Hint (level {hint_level}):"""
        
        return self.ask_ai(hint_prompt)
    
    def is_ai_working(self) -> bool:
        """Quick health check - is our AI buddy actually awake?"""
        try:
            health_check = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return health_check.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> list:
        """See what AI models you've got installed locally"""
        try:
            models_response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if models_response.status_code == 200:
                models_data = models_response.json()
                return [model['name'] for model in models_data.get('models', [])]
            return []
        except:
            return []
