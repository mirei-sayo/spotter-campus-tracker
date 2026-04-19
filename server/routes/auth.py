from fastapi import APIRouter, HTTPException
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import supabase, create_profile, get_profile
from models import SignupRequest, LoginRequest

load_dotenv()

router = APIRouter()

SECRET_KEY = os.environ.get("SECRET_KEY", "changeme")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/signup")
async def signup(body: SignupRequest):
    """Register a new Student or Finder account."""
    try:
        res = supabase.auth.sign_up({"email": body.email, "password": body.password})
        user = res.user
        if not user:
            raise HTTPException(status_code=400, detail="Signup failed — check your email/password.")

        # Create the profile row
        create_profile(
            user_id=user.id,
            email=body.email,
            full_name=body.full_name,
            role=body.role,
            student_id=body.student_id,
        )

        token = create_access_token(user.id)
        return {"access_token": token, "token_type": "bearer", "role": body.role}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(body: LoginRequest):
    """Login and receive a JWT token."""
    try:
        res = supabase.auth.sign_in_with_password({"email": body.email, "password": body.password})
        user = res.user
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        profile = get_profile(user.id)
        token = create_access_token(user.id)

        return {
            "access_token": token,
            "token_type": "bearer",
            "role": profile.get("role"),
            "full_name": profile.get("full_name"),
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/me")
async def get_me(current_user: dict = None):
    """Return the currently authenticated user's profile."""
    # Uses middleware — wired in main.py
    return current_user
