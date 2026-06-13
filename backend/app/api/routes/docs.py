from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.parser import SourceCodeParser
from app.repositories.job_repository import JobRepository
from app.core.db import get_supabase
from app.schemas.job import JobResponse

router = APIRouter()

def get_job_repo():
    return JobRepository(get_supabase())

@router.post("/analyze")
async def analyze_file(file: UploadFile = File(...), repo: JobRepository = Depends(get_job_repo)):
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
    
    # Persist as PENDING in Database
    job_id = repo.create_job(file.filename, parsed_data["sanitized_content"])
    
    return {
        "job_id": job_id,
        "status": "PENDING",
        "message": "Job created successfully. It will be processed shortly."
    }

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str, repo: JobRepository = Depends(get_job_repo)):
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
