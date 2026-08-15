from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from core.database import create_user, authenticate_user, get_user_by_id
from api.dependencies import get_current_user

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

router = APIRouter()

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@router.post("/register", response_model=dict)
async def register(data: RegisterRequest):
    ok, msg = create_user(data.name, data.email, data.password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    user = authenticate_user(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user["id"])}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"id": current_user["id"], "name": current_user["name"], "email": current_user["email"]}
