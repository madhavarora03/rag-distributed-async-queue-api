from fastapi import FastAPI

from .routers import auth, upload

app = FastAPI()

app.include_router(auth.router)
app.include_router(upload.router)


@app.get("/api/health", tags=["health"])
async def health_check():
    return {"message": "All OK!"}
