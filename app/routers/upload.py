from fastapi import APIRouter, File, HTTPException, UploadFile
from ..core.utils import save_to_tmp

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type")

    content = await file.read()
    file_path = save_to_tmp(content, file.filename)

    print(file_path)

    return {"message": "File uploaded successfully"}
