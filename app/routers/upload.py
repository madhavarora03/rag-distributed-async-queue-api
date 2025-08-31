import uuid

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.services.db_service import create_job

from ..core.utils import process_file, save_to_tmp

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("", status_code=202)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type")

    job_id = str(uuid.uuid4())

    content = await file.read()
    file_path = save_to_tmp(content, file.filename)

    # Create new job in db
    create_job(job_id, file_path)

    # Add a new task to process file in bg
    background_tasks.add_task(process_file, file_path, job_id)

    return {"job_id": job_id, "message": "Upload started"}
