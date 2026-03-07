from fastapi import APIRouter,Depends,UploadFile,File
from .service import ChatService
from .deps import get_chat_service
from .schemas import Conversationrequest
from app.core.dependencies import get_current_user
from .schemas import ConversationResponse
import aiofiles
chat_router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@chat_router.post("/create-conversation")
async def create_conversation(data:Conversationrequest,current_user=Depends(get_current_user),service:ChatService=Depends(get_chat_service)):
    current_user = current_user.id
    return await service.create_conversation(data,current_user)

#get all conversations for currently logged in user
@chat_router.get("/get-conversations",response_model=list[ConversationResponse])
async def get_conversation(current_user=Depends(get_current_user),service:ChatService=Depends(get_chat_service)):
      return await service.get_conversation(current_user.id)
#get conversation by id
@chat_router.get("/{conversation_id}",response_model=ConversationResponse)
async def conversation_by_id(conversation_id: int,current_user=Depends(get_current_user),service:ChatService=Depends(get_chat_service)):
        return await service.conversation_by_id(current_user.id,conversation_id)

#add participants
@chat_router.post("/{conversation_id}/add/{user_id}")
async def add_participants(conversation_id:int,user_id:int,service:ChatService=Depends(get_chat_service)):
      return await service.add_participants(conversation_id,user_id)


#remove participants
@chat_router.delete("/{conversation_id}/delete/{user_id}")
async def remove_participants(conversation_id:int,user_id:int,service:ChatService=Depends(get_chat_service)):
      return await service.removeparticipants(conversation_id,user_id)

# delete conversation
@chat_router.delete("/{conversation_id}")
async def delete_conversation(conversation_id:int,current_user=Depends(get_current_user),service:ChatService=Depends(get_chat_service)):
      return await service.delete_conversation(conversation_id,current_user.id)


# messaging apis
@chat_router.post("/upload/{conversation_id}")
async def upload_file(conversation_id:int,
                      current_user=Depends(get_current_user),
                      service:ChatService=Depends(get_chat_service),
                      files:UploadFile=File(...)):
     return await service.upload_file(conversation_id,current_user,files)

async def download_stream(filename:str,
                          conversation_id:int,
                      current_user=Depends(get_current_user),
                      service:ChatService=Depends(get_chat_service)):
      return await service.download_stream(conversation_id,current_user,filename)

@chat_router.get("/messages/{conversation_id}")
async def get_messages(conversation_id:int,page:int,limit:int,
                      service:ChatService=Depends(get_chat_service)):
      return await service.get_messages(conversation_id,page,limit)