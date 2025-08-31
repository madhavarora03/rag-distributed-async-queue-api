import asyncio
import os
import tempfile
import uuid
from typing import Tuple

from ..services.db_service import JobStatus, update_job
from ..services.r2_client import r2_client
from .config import settings


def save_to_tmp(file: bytes, file_name: str | None) -> Tuple[str, str]:
    """
    Save bytes securely in the system's temp dir with a unique name.
    Returns the absolute file path.
    """
    tmp_dir = tempfile.gettempdir()
    base_name = os.path.basename(file_name) if file_name else "uploaded_file"
    unique_name = f"{uuid.uuid4()}_{base_name}"

    file_path = os.path.join(tmp_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(file)

    return file_path, unique_name


def save_to_r2(file_path: str) -> None:
    R2_BUCKET_NAME = settings.r2_bucket_name
    if R2_BUCKET_NAME is None:
        raise ValueError("R2_BUCKET_NAME is not set")

    try:
        r2_client.upload_file(file_path, R2_BUCKET_NAME,
                              os.path.basename(file_path))
    except Exception as e:
        print(f"Error uploading file to S3: {e}")


async def process_file(file_path: str, job_id: str):
    try:
        steps = [
            ("Saving to R2", lambda: save_to_r2(file_path)),
            ("Parsing PDF", lambda: asyncio.sleep(2)),
            ("Generating embeddings", lambda: asyncio.sleep(2)),
            ("Storing in vector DB", lambda: asyncio.sleep(1)),
        ]

        for step, action in steps:
            update_job(job_id, status=JobStatus.PROCESSING, step=step)
            await asyncio.to_thread(action)
            await asyncio.sleep(0.1)

        update_job(job_id, status=JobStatus.DONE, step="Complete")

    except Exception as e:
        update_job(job_id, status=JobStatus.FAILED, step="Error", error=str(e))
