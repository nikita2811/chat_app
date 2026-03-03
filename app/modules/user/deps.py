from .service import UserService
from .repository import UserRepository
from fastapi import Depends
from app.core.database import get_db

def get_user_repo(db=Depends(get_db)):
    return UserRepository(db)

def get_user_service(repo=Depends(get_user_repo)):
    return UserService(repo)