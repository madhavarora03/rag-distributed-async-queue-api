from dotenv import load_dotenv
from fastapi import FastAPI

from .routers import upload

load_dotenv()

app = FastAPI()

app.include_router(upload.router)


@app.get("/api/health", tags=["health"])
async def health_check():
    return {"message": "All OK!"}
