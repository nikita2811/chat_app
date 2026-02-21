from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

def _prehash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password:str):
    prehashed = _prehash(password)
    return pwd_context.hash(prehashed)

def verify_password(plain_password:str,hashed_password:str):
    prehashed = _prehash(plain_password)
    return pwd_context.verify(prehashed,hashed_password)