from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Annotated
import re
import random
from jose import JWTError, jwt
from passlib.context import CryptContext
from .. import models
from ..database import get_db
from ..services.email import send_verification_email
from pydantic import BaseModel, EmailStr, Field, validator

# JWT settings
SECRET_KEY = "your-secret-key"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/auth", tags=["认证"])

class UserCreate(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

class VerifyEmail(BaseModel):
    email: EmailStr
    code: str = Field(pattern="^[0-9]{6}$")

class Login(BaseModel):
    email: EmailStr
    password: str

from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Generate verification code
    code = ''.join(random.choices('0123456789', k=6))
    verification = models.Verification(
        user_id=db_user.id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(verification)
    db.commit()

    # Send verification email
    await send_verification_email(user.email, code)

    return {"message": "Registration successful. Please check your email for verification code."}

@router.post("/verify-email")
async def verify_email(verify: VerifyEmail, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == verify.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    verification = db.query(models.Verification)\
        .filter(models.Verification.user_id == user.id)\
        .order_by(models.Verification.created_at.desc())\
        .first()

    if not verification or verification.code != verify.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

    if verification.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired"
        )

    user.is_verified = True
    db.commit()

    return {"message": "Email verified successfully"}

@router.post("/login", response_model=Token)
async def login(login_data: Login, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified"
        )


    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

class EmailRequest(BaseModel):
    email: EmailStr

@router.post("/resend-verification")
async def resend_verification(email_data: EmailRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    # Check rate limiting
    fifteen_mins_ago = datetime.utcnow() - timedelta(minutes=15)
    attempt_count = db.query(models.Verification)\
        .filter(
            models.Verification.user_id == user.id,
            models.Verification.created_at > fifteen_mins_ago
        ).count()

    if attempt_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many verification attempts. Please try again later."
        )

    # Generate new verification code
    code = ''.join(random.choices('0123456789', k=6))
    verification = models.Verification(
        user_id=user.id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(verification)
    db.commit()

    # Send verification email
    await send_verification_email(email_data.email, code)

    return {"message": "Verification code sent", "code": code}
