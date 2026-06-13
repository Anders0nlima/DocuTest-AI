from supabase import Client
from typing import Optional, Dict, Any
from app.schemas.job import JobStatus
from app.schemas.generation import GenerationResult

class JobRepository:
    def __init__(self, db_client: Client):
        self.db = db_client

    def create_job(self, filename: str, original_code: str) -> str:
        """Creates a new job in PENDING status and returns the UUID."""
        data = {
            "filename": filename,
            "status": JobStatus.PENDING.value,
            "original_code": original_code
        }
        response = self.db.table("jobs").insert(data).execute()
        return response.data[0]["id"]

    def update_job_success(self, job_id: str, result: GenerationResult) -> None:
        """Updates the job status to COMPLETED and saves the generated result."""
        data = {
            "status": JobStatus.COMPLETED.value,
            "result": result.model_dump()
        }
        self.db.table("jobs").update(data).eq("id", job_id).execute()

    def update_job_failure(self, job_id: str, error_message: str) -> None:
        """Updates the job status to FAILED and records the error message."""
        data = {
            "status": JobStatus.FAILED.value,
            "error_message": error_message
        }
        self.db.table("jobs").update(data).eq("id", job_id).execute()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a job by its ID."""
        response = self.db.table("jobs").select("*").eq("id", job_id).execute()
        if not response.data:
            return None
        return response.data[0]

    def get_all_jobs(self) -> list[Dict[str, Any]]:
        """Retrieves all jobs, ordered by creation date descending."""
        response = self.db.table("jobs").select("id, filename, status, created_at").order("created_at", desc=True).execute()
        return response.data
