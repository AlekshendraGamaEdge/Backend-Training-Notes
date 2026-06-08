from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class UserResponse(BaseModel):
    email: str
    full_name: str
    created_at: str

