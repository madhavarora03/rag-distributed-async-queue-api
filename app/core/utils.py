import os
import tempfile
import uuid


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
