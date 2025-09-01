from fastapi import APIRouter, Query, Path, Depends
from ..queue.connection import queue
from ..queue.worker import process_query
from ..services.db_service import save_conversation
from .auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
def chat(
    query: str = Query(..., description="Chat message"),
    current_user: str = Depends(get_current_user)
):
    job = queue.enqueue(process_query, query, meta={"username": current_user})
    return {"status": "queued", "job_id": job.id}


@router.get("/result/{job_id}")
def get_result(
    job_id: str = Path(..., description="Job ID"),
    current_user: str = Depends(get_current_user)
):
    job = queue.fetch_job(job_id=job_id)
    if not job or not job.result:
        return {"status": "pending or not found", "job_id": job_id}

    # Save query/response under this user
    query = job.args[0]  # original query
    response = job.result
    save_conversation(current_user, query, response)

    return {"result": response}
