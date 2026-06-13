from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.db.client import get_db
from app.core.auth import create_access_token
from app.services.email import send_verification_email, send_password_reset_email
import secrets
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
limiter = Limiter(key_func=get_remote_address)

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/register", status_code=201)
@limiter.limit("5/minute")
def register(request: Request, body: RegisterRequest):
    db = get_db()
    existing = db.table("users").select("id").eq("email", body.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="An account with this email already exists")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    user_id = str(uuid.uuid4())
    hashed_password = pwd_context.hash(body.password)
    verification_token = secrets.token_urlsafe(32)
    db.table("users").insert({
        "id": user_id,
        "name": body.name,
        "email": body.email,
        "password_hash": hashed_password,
        "verification_token": verification_token,
        "is_verified": True,  # Auto-verify in dev — re-enable after Resend domain setup
    }).execute()
    # send_verification_email(body.email, verification_token, body.name)
    return {"message": "Account created successfully. You can now sign in."}

@router.get("/verify")
def verify_email(token: str):
    db = get_db()
    result = db.table("users").select("id, is_verified").eq("verification_token", token).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")
    user = result.data[0]
    if user["is_verified"]:
        return {"message": "Account already verified"}
    db.table("users").update({
        "is_verified": True,
        "verification_token": None
    }).eq("id", user["id"]).execute()
    return {"message": "Email verified successfully. You can now sign in."}

@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, body: LoginRequest):
    db = get_db()
    result = db.table("users").select("*").eq("email", body.email).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    user = result.data[0]
    if not pwd_context.verify(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user["is_verified"]:
        raise HTTPException(status_code=403, detail="Please verify your email before signing in")
    token = create_access_token({"sub": user["id"], "email": user["email"], "name": user["name"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]}
    }

@router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, body: ForgotPasswordRequest):
    db = get_db()
    result = db.table("users").select("id, name").eq("email", body.email).execute()
    if result.data:
        reset_token = secrets.token_urlsafe(32)
        db.table("users").update({"reset_token": reset_token}).eq("email", body.email).execute()
        send_password_reset_email(body.email, reset_token)
    return {"message": "If an account exists with that email, a reset link has been sent."}

@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest):
    db = get_db()
    result = db.table("users").select("id").eq("reset_token", body.token).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    hashed = pwd_context.hash(body.new_password)
    db.table("users").update({
        "password_hash": hashed,
        "reset_token": None
    }).eq("reset_token", body.token).execute()
    return {"message": "Password reset successfully. You can now sign in."}