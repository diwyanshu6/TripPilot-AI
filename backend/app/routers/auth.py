import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from app.database.connection import Database
from app.utils.security import hash_password, verify_password, create_jwt_token
from app.utils.deps import get_current_user

router = APIRouter(prefix="", tags=["Authentication"])

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(data: RegisterSchema):
    # Check if email exists
    existing = Database.fetch_one("SELECT * FROM users WHERE email = %s", (data.email,))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed = hash_password(data.password)
    user_id = str(uuid.uuid4())
    
    try:
        # Check database type using connection pool existence
        if Database._pool:
            # PostgreSQL gen_random_uuid is default, but let's supply user_id to be safe
            Database.execute(
                "INSERT INTO users (id, name, email, password) VALUES (%s, %s, %s, %s)",
                (user_id, data.name, data.email, hashed)
            )
        else:
            Database.execute(
                "INSERT INTO users (id, name, email, password) VALUES (%s, %s, %s, %s)",
                (user_id, data.name, data.email, hashed)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {e}"
        )
        
    token = create_jwt_token({"user_id": user_id, "email": data.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "name": data.name, "email": data.email}
    }

@router.post("/login")
def login(data: LoginSchema):
    user = Database.fetch_one("SELECT * FROM users WHERE email = %s", (data.email,))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
        
    if not verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
        
    token = create_jwt_token({"user_id": str(user["id"]), "email": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": str(user["id"]), "name": user["name"], "email": user["email"]}
    }

@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    user = Database.fetch_one("SELECT id, name, email FROM users WHERE id = %s", (current_user["user_id"],))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
