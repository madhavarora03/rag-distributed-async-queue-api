from fastapi import APIRouter, Query, Path
from ..queue.connection import queue
from ..queue.worker import process_query

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
def chat(query: str = Query(..., description="Chat message")):
    job = queue.enqueue(process_query, query)
    return {"status": "queued", "job_id": job.id}


@router.get("/result/{job_id}")
def get_result(job_id: str = Path(..., description="Job ID")):
    job = queue.fetch_job(job_id=job_id)
    if not job or not job.result:
        return {"status": "pending or not found", "job_id": job_id}
    return {"result": job.result}
