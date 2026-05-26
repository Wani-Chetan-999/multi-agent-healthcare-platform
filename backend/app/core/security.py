from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Initialize independent cryptographic contexts
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """
    Generate secure bcrypt hash.
    bcrypt supports maximum 72 bytes.
    """

    if len(password.encode("utf-8")) > 72:
        raise ValueError(
            "Password exceeds bcrypt maximum length of 72 bytes."
        )

    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext input password against an existing database hash.
    """
    # Enforce safe utf-8 byte conversion before passing to passlib/bcrypt
    plain_password_bytes = plain_password.encode("utf-8")
    return pwd_context.verify(plain_password_bytes, hashed_password)

def create_access_token(subject: Union[str, Any], expires_delta: Union[timedelta, None] = None) -> str:
    """
    Generates a cryptographically signed JWT token containing user identity details.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt