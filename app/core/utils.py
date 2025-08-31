import os
import tempfile
import uuid

from .config import settings
from .r2_client import r2_client


def save_to_tmp(file: bytes, file_name: str | None) -> str:
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

    return file_path


def save_to_r2(file_path: str) -> None:
    R2_BUCKET_NAME = settings.r2_bucket_name
    if R2_BUCKET_NAME is None:
        raise ValueError("R2_BUCKET_NAME is not set")

    try:
        r2_client.upload_file(file_path, R2_BUCKET_NAME,
                              os.path.basename(file_path))
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
