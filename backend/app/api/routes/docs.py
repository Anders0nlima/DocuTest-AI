from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from app.services.parser import SourceCodeParser
from app.repositories.job_repository import JobRepository
from app.core.db import get_supabase
from app.schemas.job import JobResponse
from app.services.llm_provider import AIGeneratorProvider, get_llm_provider

router = APIRouter()

def get_job_repo():
    return JobRepository(get_supabase())

async def process_code_analysis(job_id: str, sanitized_code: str, repo: JobRepository, llm: AIGeneratorProvider):
    """Background task to call LLM and update DB without blocking the HTTP request."""
    try:
        result = await llm.generate(sanitized_code)
        repo.update_job_success(job_id, result)
    except Exception as e:
        repo.update_job_failure(job_id, str(e))

@router.post("/analyze")
async def analyze_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    repo: JobRepository = Depends(get_job_repo),
    llm: AIGeneratorProvider = Depends(get_llm_provider)
):
    if not file.filename.endswith((".py", ".js", ".ts")):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file extension. Only .py, .js, .ts are allowed."
        )
    
    content = await file.read()
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text.")
    
    parsed_data = SourceCodeParser.parse(text_content)
    sanitized_code = parsed_data["sanitized_content"]
    
    # 1. Persist as PENDING in Database
    job_id = repo.create_job(file.filename, sanitized_code)
    
    # 2. Orchestrate AI Generation in Background
    background_tasks.add_task(process_code_analysis, job_id, sanitized_code, repo, llm)
    
    return {
        "job_id": job_id,
        "status": "PENDING",
        "message": "Job created successfully. It will be processed in the background."
    }

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str, repo: JobRepository = Depends(get_job_repo)):
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
