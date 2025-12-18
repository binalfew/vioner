"""
Authentication Router - JWT-based authentication for the NER System.

Provides:
- User registration with database persistence
- Login with JWT token generation
- Token refresh
- Password hashing with SHA256
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
import hashlib
import hmac
import base64
import json
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=2)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class User(BaseModel):
    id: str
    email: str
    name: str
    role: str
    created_at: str


class UserResponse(BaseModel):
    user: User
    message: str


# Password hashing
def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt."""
    salt = SECRET_KEY[:16]
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return hash_password(plain_password) == hashed_password


# JWT implementation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire.timestamp(), "iat": datetime.utcnow().timestamp()})

    header = base64.urlsafe_b64encode(json.dumps({"alg": ALGORITHM, "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps(to_encode, default=str).encode()).decode().rstrip("=")
    signature = hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).hexdigest()

    return f"{header}.{payload}.{signature}"


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header, payload, signature = parts

        # Verify signature
        expected_signature = hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).hexdigest()
        if signature != expected_signature:
            return None

        # Decode payload
        payload += "=" * (4 - len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))

        # Check expiration
        if data.get("exp", 0) < datetime.utcnow().timestamp():
            return None

        return data
    except Exception:
        return None


def get_db_session():
    """Get database session."""
    from database.connection import get_db_context
    return get_db_context


def get_user_by_email(db, email: str):
    """Get user by email from database."""
    from database.models import UserDB
    return db.query(UserDB).filter(UserDB.email == email).first()


def get_user_by_id(db, user_id: str):
    """Get user by user_id from database."""
    from database.models import UserDB
    return db.query(UserDB).filter(UserDB.user_id == user_id).first()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, request: Request):
    """Register a new user."""
    get_db_context = get_db_session()

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Check if email already exists
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        from database.models import UserDB

        # Create user
        user_id = hashlib.md5(user_data.email.encode()).hexdigest()[:12]
        new_user = UserDB(
            user_id=user_id,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            name=user_data.name,
            role="user",
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"New user registered: {user_data.email}")

        return UserResponse(
            user=User(
                id=new_user.user_id,
                email=new_user.email,
                name=new_user.name,
                role=new_user.role,
                created_at=new_user.created_at.isoformat()
            ),
            message="User registered successfully"
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token (OAuth2 form)."""
    get_db_context = get_db_session()

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        user = get_user_by_email(db, form_data.username)

        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.user_id},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return Token(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.user_id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        )


@router.post("/login/json", response_model=Token)
async def login_json(credentials: UserLogin, request: Request):
    """Login with JSON body instead of form data."""
    get_db_context = get_db_session()

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        user = get_user_by_email(db, credentials.email)

        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.user_id},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return Token(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.user_id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        )


@router.get("/me", response_model=User)
async def get_me(request: Request):
    """Get current user profile."""
    # Get token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    get_db_context = get_db_session()

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        user = get_user_by_email(db, payload.get("sub"))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return User(
            id=user.user_id,
            email=user.email,
            name=user.name,
            role=user.role,
            created_at=user.created_at.isoformat()
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request):
    """Refresh access token."""
    # Get token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    get_db_context = get_db_session()

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        user = get_user_by_email(db, payload.get("sub"))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.user_id},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return Token(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.user_id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        )


def init_demo_user():
    """Initialize demo user in database if not exists."""
    try:
        get_db_context = get_db_session()

        with get_db_context() as db:
            if db is None:
                logger.warning("Database not available for demo user initialization")
                return

            from database.models import UserDB

            demo_email = "demo@example.com"
            existing = db.query(UserDB).filter(UserDB.email == demo_email).first()

            if not existing:
                demo_user = UserDB(
                    user_id="demo123",
                    email=demo_email,
                    password_hash=hash_password("demo123"),
                    name="Demo User",
                    role="admin",
                    is_active=True
                )
                db.add(demo_user)
                db.commit()
                logger.info("Demo user created: demo@example.com / demo123")
            else:
                logger.info("Demo user already exists")

    except Exception as e:
        logger.error(f"Failed to initialize demo user: {e}")


# Initialize demo user on module load
# Note: This will be called when the router is imported
# The actual initialization happens in main.py startup event
