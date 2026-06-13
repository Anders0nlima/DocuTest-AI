from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.parser import SourceCodeParser
from app.repositories.job_repository import JobRepository
from app.core.db import get_supabase
from app.schemas.job import JobResponse
from app.services.llm_provider import AIGeneratorProvider, get_llm_provider

router = APIRouter()

def get_job_repo():
    return JobRepository(get_supabase())

@router.post("/analyze")
async def analyze_file(
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
    
    # 2. Orchestrate AI Generation
    try:
        result = await llm.generate(sanitized_code)
        # 3. Update Database to COMPLETED
        repo.update_job_success(job_id, result)
    except Exception as e:
        # 4. Update Database to FAILED on errors
        repo.update_job_failure(job_id, str(e))
    
    return {
        "job_id": job_id,
        "status": "PROCESSED",
        "message": "Job processed successfully."
    }

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str, repo: JobRepository = Depends(get_job_repo)):
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
