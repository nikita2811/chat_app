from app.modules.chat.service import ChatService
from app.modules.chat.repository import ChatRepository
from app.core.database import get_db
from fastapi import Depends

def get_chat_repo(db=Depends(get_db)):
    return ChatRepository(db)

def get_chat_service(repo:ChatRepository=Depends(get_chat_repo)):
    return ChatService(repo)

