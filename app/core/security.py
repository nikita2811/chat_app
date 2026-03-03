import secrets
from datetime import datetime,timedelta
from jose import jwt
import hashlib
from app.core.config import settings



def generate_token():
    return secrets.token_urlsafe(32)


def token_expiry():
    return datetime.utcnow() + timedelta(hours=24)

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_EXPIRE_MIN)
    to_encode.update({"exp": expire,"type":"access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_EXPIRE_DAYS)
    data.update({"exp": expire, "type": "refresh"})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

def hash_token(token:str):
     return hashlib.sha256(token.encode()).hexdigest()

def create_reset_token(email:str):
    payload = {
        "sub":email,
        "exp":datetime.utcnow()+timedelta(hours=1)
    }
    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

