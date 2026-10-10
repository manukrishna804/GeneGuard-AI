from datetime import datetime, timedelta
from typing import Optional
import hashlib
import hmac
import os
import jwt
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

# In production, this should be in .env and loaded via settings
SECRET_KEY = "geneguard-super-secret-key-for-jwt-signing"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def _hash_password(password: str, salt: str) -> str:
    """SHA-256 based password hashing with salt."""
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def get_password_hash(password: str) -> str:
    """Generate a salted SHA-256 hash of the password."""
    salt = os.urandom(32).hex()
    hashed = _hash_password(password, salt)
    return f"{salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored salted hash."""
    try:
        salt, stored_hash = hashed_password.split("$", 1)
        expected_hash = _hash_password(plain_password, salt)
        return hmac.compare_digest(expected_hash, stored_hash)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt