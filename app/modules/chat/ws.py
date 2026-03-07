from fastapi import APIRouter,WebSocket,WebSocketDisconnect,Query,Depends
from typing import Dict,List
from app.core.database import get_db
from .models import Message,Conversation
import json
from datetime import datetime
from loguru import logger
import jwt
from app.core.config import settings
from sqlalchemy import update
router = APIRouter()
logger.info("websocket init")
class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[int,List[WebSocket]]={}

    async def connect(self,conversation_id:int,websocket:WebSocket):
        await websocket.accept()
        logger.info("user connected to conversation {}", conversation_id)
        self.rooms.setdefault(conversation_id,[]).append(websocket)


    async def disconnect(self,conversation_id:int,websocket:WebSocket):
        if conversation_id in self.rooms:
            self.rooms[conversation_id].remove(websocket)
    

    async def broadcast(self,conversation_id:int,message:dict):
        logger.info(message)
        dead_connections = []

        for ws in self.rooms.get(conversation_id,[]):
            try:
                await ws.send_json(message)
            except RuntimeError:
                # websocket already closed — mark for cleanup
                logger.warning("dead websocket in room {} — removing", conversation_id)
                dead_connections.append(ws)
            except Exception as e:
                logger.exception("failed to send to websocket in room {}", conversation_id)
                dead_connections.append(ws)
            
             # clean up dead connections
        for ws in dead_connections:
            try:
                self.rooms[conversation_id].remove(ws)
            except (ValueError, KeyError):
                pass


manager = ConnectionManager()

@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint( websocket: WebSocket,
    conversation_id: int,
    user_id: int = Query(...),
    username: str = Query(...),
    token: str = Query(...),
     db=Depends(get_db) ):
    if token.startswith("Bearer "):
            token = token[7:]
    
    try:
     payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
     token_user_id = int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
     logger.error("token expired")
     await websocket.close(code=1008)
     return
    except jwt.InvalidTokenError as e:
      logger.error("invalid token — {}", str(e))
      await websocket.close(code=1008)
      return

   
    logger.info("token valid — user_id={}", token_user_id)
    await manager.connect(conversation_id,websocket)
    await manager.broadcast(conversation_id,{
        "type": "system",
        "content": f"{username} joined the room",
        "timestamp": str(datetime.utcnow())
    })
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "text":
                 content = data.get("content", "").strip()
                 if not content:
                    continue
                 msg = Message(
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    content=content
                 )
                 db.add(msg)
                 await db.commit()
                 await db.refresh(msg)
                
                  # Broadcast to room
                 await manager.broadcast(conversation_id, {
                    "type": "text",
                    "id": msg.id,
                    "sender_id": user_id,
                    "username": username,
                    "content": content,
                    "timestamp": str(datetime.utcnow())
                })

            elif msg_type == "file_notify":
                file_url = data.get("file_url")
                file_name = data.get("file_name")

                await manager.broadcast(conversation_id, {
                    "type": "file",
                    "sender_id": user_id,
                    "username": username,
                    "file_url": file_url,
                    "file_name": file_name,
                    "timestamp": str(datetime.utcnow())
                })
                chat_count = await db.execute(update(Conversation).where(Conversation.id ==conversation_id).values(chat_count = Conversation.chat_count+1))
                await db.commit()
                await db.refresh(chat_count)



    except WebSocketDisconnect:
         await manager.disconnect(conversation_id, websocket)
         await manager.broadcast(conversation_id, {
            "type": "system",
            "content": f"{username} left the room",
            "timestamp": str(datetime.utcnow())
        })
