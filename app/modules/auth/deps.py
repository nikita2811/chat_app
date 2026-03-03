from .repository import AuthRepository
from app.core.database import get_db
from fastapi import Depends
from .service import AuthService

def get_auth_repository(db=Depends(get_db)):
    return AuthRepository(db)

def get_auth_service(repo:AuthRepository = Depends(get_auth_repository)):
    return AuthService(repo)