from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from ..core.security import (ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token,
                             decode_access_token, get_password_hash,
                             verify_password)
from ..services.db_service import users

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# --- Schemas ---
class SignupRequest(BaseModel):
    username: str
    password: str


@router.post("", status_code=201)
def signup(payload: SignupRequest):
    """Register a new user."""
    # Check if user exists
    if users.find_one({"username": payload.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Hash password
    hashed_pw = get_password_hash(payload.password)

    # Insert into Mongo
    users.insert_one({
        "username": payload.username,
        "hashed_password": hashed_pw,
        "created_at": datetime.now()
    })

    return {"message": "User created successfully"}


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users.find_one({"username": form_data.username})
    if not user or not verify_password(
            form_data.password,
            user["hashed_password"]
    ):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload["sub"]
