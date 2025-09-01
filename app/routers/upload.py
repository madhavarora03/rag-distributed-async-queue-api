import asyncio
import uuid

from fastapi import (APIRouter, BackgroundTasks, File, HTTPException, Response,
                     UploadFile)

from ..core.utils import save_to_tmp, start_process_file
from ..services.db_service import create_job, get_job

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("", status_code=202)
async def upload_file(
    background_tasks: BackgroundTasks,
    response: Response,
    file: UploadFile = File(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type")

    job_id = str(uuid.uuid4())

    content = await file.read()
    file_path, unique_name = save_to_tmp(content, file.filename)

    # Create new job in db
    create_job(job_id, unique_name)

    # Add a new task to process file in bg
    background_tasks.add_task(start_process_file, file_path, job_id)

    response.headers["Location"] = f"/api/upload/status/{job_id}"
    return {"job_id": job_id, "message": "Upload started"}


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    job = await asyncio.to_thread(get_job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
