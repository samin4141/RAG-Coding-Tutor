from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import random
from sqlalchemy.orm import Session

from core.database import get_db, Problem, Solution, TestCase, Attempt
from core.llm_client import LLMClient
from services.code_executor import CodeExecutor

router = APIRouter()

class PracticeStartRequest(BaseModel):
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    skills: Optional[List[str]] = None

class PracticeStartResponse(BaseModel):
    problem_id: str
    title: str
    difficulty: str
    prompt_md: str
    sample_tests: List[Dict[str, Any]]
    tags: List[str]
    skills: List[str]

class SubmitCodeRequest(BaseModel):
    problem_id: str
    code: str
    language: str = "python"

class TestResult(BaseModel):
    input_data: str
    expected_output: str
    actual_output: str
    passed: bool
    error: Optional[str] = None

class SubmitCodeResponse(BaseModel):
    passed: bool
    score: float
    test_results: List[TestResult]
    feedback_md: str
    attempt_id: str

class HintRequest(BaseModel):
    problem_id: str
    hint_level: int = 1

@router.post("/start", response_model=PracticeStartResponse)
async def start_practice(
    request: PracticeStartRequest,
    db: Session = Depends(get_db)
):
    """Pick a coding problem to work on - let's get this practice session started!"""
    try:
        # Let's build a query to find the perfect problem for you
        query = db.query(Problem)
        
        if request.difficulty:
            query = query.filter(Problem.difficulty == request.difficulty)
        
        if request.skills:
            # Filter by the skills you want to practice
            for skill in request.skills:
                query = query.filter(Problem.skills.contains([skill]))
        
        problems = query.all()
        
        if not problems:
            raise HTTPException(status_code=404, detail="No problems found matching criteria")
        
        # Pick a random problem for now (later we'll make this smarter with spaced repetition)
        problem = random.choice(problems)
        
        # Grab the test cases you can see (there are hidden ones too!)
        sample_tests = []
        for test in problem.testcases:
            if test.visible:
                sample_tests.append({
                    "input": test.input_data,
                    "expected_output": test.expected_output
                })
        
        return PracticeStartResponse(
            problem_id=problem.id,
            title=problem.title,
            difficulty=problem.difficulty,
            prompt_md=problem.prompt_md,
            sample_tests=sample_tests,
            tags=problem.tags or [],
            skills=problem.skills or []
        )
        
    except Exception as e:
        print(f"Start practice error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit", response_model=SubmitCodeResponse)
async def submit_code(
    request: SubmitCodeRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Submit your solution and see how you did - fingers crossed!"""
    try:
        llm_client: LLMClient = req.app.state.llm_client
        
        # First, let's find the problem you're working on
        problem = db.query(Problem).filter(Problem.id == request.problem_id).first()
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Grab the "perfect" solution to compare against
        canonical_solution = db.query(Solution).filter(
            Solution.problem_id == request.problem_id,
            Solution.lang == request.language
        ).first()
        
        # Time to run your code and see if it works!
        executor = CodeExecutor()
        test_results = []
        passed_count = 0
        
        for test_case in problem.testcases:
            result = await executor.execute_code(
                code=request.code,
                language=request.language,
                input_data=test_case.input_data,
                expected_output=test_case.expected_output
            )
            
            test_result = TestResult(
                input_data=test_case.input_data,
                expected_output=test_case.expected_output,
                actual_output=result.get('output', ''),
                passed=result.get('passed', False),
                error=result.get('error')
            )
            test_results.append(test_result)
            
            if test_result.passed:
                passed_count += 1
        
        # Let's see how well you did
        total_tests = len(test_results)
        score = (passed_count / total_tests) if total_tests > 0 else 0.0
        all_passed = passed_count == total_tests
        
        # Get some AI-powered feedback on your solution
        feedback_md = ""
        if canonical_solution:
            test_summary = {
                'passed': passed_count,
                'total': total_tests,
                'all_passed': all_passed
            }
            feedback_md = llm_client.generate_feedback(
                student_code=request.code,
                canonical_code=canonical_solution.code,
                problem_title=problem.title,
                test_results=test_summary
            )
        
        # Save this attempt for your records
        attempt = Attempt(
            problem_id=request.problem_id,
            lang=request.language,
            code=request.code,
            passed=all_passed,
            score=score,
            feedback_md=feedback_md
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        
        return SubmitCodeResponse(
            passed=all_passed,
            score=score,
            test_results=test_results,
            feedback_md=feedback_md,
            attempt_id=attempt.id
        )
        
    except Exception as e:
        print(f"Submit code error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hint")
async def get_hint(
    request: HintRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Stuck? Let's give you a little nudge in the right direction"""
    try:
        llm_client: LLMClient = req.app.state.llm_client
        vector_store = req.app.state.vector_store
        
        # Find the problem you need help with
        problem = db.query(Problem).filter(Problem.id == request.problem_id).first()
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Look through your notes for relevant hints
        context = ""
        if problem.skills:
            skill_query = " ".join(problem.skills)
            search_results = vector_store.search(skill_query, k=3, threshold=0.3)
            context_parts = [result['text'] for result in search_results]
            context = "\n\n".join(context_parts)
        
        # Generate a helpful hint based on what we found
        hint = llm_client.generate_hint(
            problem_prompt=problem.prompt_md,
            context=context,
            hint_level=request.hint_level
        )
        
        return {"hint": hint, "level": request.hint_level}
        
    except Exception as e:
        print(f"Hint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/problems")
async def list_problems(
    difficulty: Optional[str] = None,
    skill: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Show me all the problems I can work on"""
    try:
        query = db.query(Problem)
        
        if difficulty:
            query = query.filter(Problem.difficulty == difficulty)
        
        if skill:
            query = query.filter(Problem.skills.contains([skill]))
        
        problems = query.all()
        
        return [
            {
                "id": problem.id,
                "slug": problem.slug,
                "title": problem.title,
                "difficulty": problem.difficulty,
                "tags": problem.tags,
                "skills": problem.skills
            }
            for problem in problems
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attempts")
async def get_attempts(
    problem_id: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Let's see how you've been doing with your practice sessions"""
    try:
        query = db.query(Attempt).order_by(Attempt.created_at.desc())
        
        if problem_id:
            query = query.filter(Attempt.problem_id == problem_id)
        
        attempts = query.limit(limit).all()
        
        return [
            {
                "id": attempt.id,
                "problem_id": attempt.problem_id,
                "problem_title": attempt.problem.title if attempt.problem else "Unknown",
                "lang": attempt.lang,
                "passed": attempt.passed,
                "score": attempt.score,
                "created_at": attempt.created_at.isoformat()
            }
            for attempt in attempts
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_practice_stats(db: Session = Depends(get_db)):
    """Show me some stats about my coding practice journey"""
    try:
        total_problems = db.query(Problem).count()
        total_attempts = db.query(Attempt).count()
        passed_attempts = db.query(Attempt).filter(Attempt.passed == True).count()
        
        success_rate = (passed_attempts / total_attempts) if total_attempts > 0 else 0.0
        
        return {
            "total_problems": total_problems,
            "total_attempts": total_attempts,
            "passed_attempts": passed_attempts,
            "success_rate": success_rate
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
