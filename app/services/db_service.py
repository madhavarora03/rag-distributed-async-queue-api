from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pymongo import ASCENDING, MongoClient

from ..core.config import settings


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


client = MongoClient(
    f"mongodb://{settings.mongo_user}:{settings.mongo_pass}@"
    f"{settings.mongo_host}:{settings.mongo_port}",
    maxPoolSize=10,  # connection pooling
)

db = client[settings.db_name]

jobs = db["jobs"]
users = db["users"]

# Ensure useful indexes
jobs.create_index([("job_id", ASCENDING)], unique=True)
jobs.create_index([("owner", ASCENDING)])
jobs.create_index([("status", ASCENDING)])


def create_job(job_id: str, filename: str, owner_id: str) -> None:
    """Insert a new job into MongoDB."""
    jobs.insert_one({
        "owner": owner_id,  # username
        "job_id": job_id,
        "filename": filename,
        "status": JobStatus.PENDING.value,
        "step": None,
        "error": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })


def update_job(job_id: str, status: JobStatus, step: Optional[str] = None,
               error: Optional[str] = None) -> bool:
    """Update job status. Returns True if modified, False if not found."""
    result = jobs.update_one(
        {"job_id": job_id},
        {"$set": {
            "status": status.value,
            "step": step,
            "error": error,
            "updated_at": datetime.now()
        }}
    )
    return result.modified_count > 0


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Fetch job by ID, excluding Mongo's _id field."""
    job = jobs.find_one({"job_id": job_id}, {"_id": 0})
    return job


def get_user_id(username: str) -> Optional[str]:
    user = users.find_one({"username": username}, {"_id": 1})
    return user["_id"] if user else None
