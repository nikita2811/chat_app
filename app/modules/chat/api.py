from fastapi import APIRouter,Depends
from .service import ChatService
from .deps import get_chat_service

chat_router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@chat_router.post("/conversation")
async def create_conversation(service:ChatService=Depends(get_chat_service)):
    return await service.create_conversation()

