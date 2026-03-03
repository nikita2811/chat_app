from fastapi import APIRouter,WebSocket,WebSocketDisconnect,Query
from typing import Dict,List
from database import database
from .models import messages
import json
from datetime import datetime

app = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.rooms=Dict[int,List[WebSocket]]={}

    async def connect(self,conversation_id:int,websocket:WebSocket):
        await websocket.accept()
        self.rooms.setdefault(conversation_id,[]).append(websocket)


    async def disconnect(self,conversation_id:int,websocket:WebSocket):
        if conversation_id in self.rooms:
            self.rooms[conversation_id].remove(websocket)
    

    async def broadcast(self,conversation_id:int,message:dict):
        for ws in self.rooms.get(conversation_id,[]):
            await ws.send_json(message)


manager = ConnectionManager()

@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint( websocket: WebSocket,
    conversation_id: int,
    user_id: int = Query(...),
    username: str = Query(...)):
    await manager.connect(conversation_id,websocket)
    await manager.broadcast(conversation_id,{
        "type": "system",
        "content": f"{username} joined the room",
        "timestamp": str(datetime.utcnow())
    })
    try:
        while True:
            data = await websocket.recieve_json()
            msg_type = data.get("type")

            if msg_type == "text":
                 content = data.get("content", "").strip()
                 if not content:
                    continue
                 query = messages.insert().values(
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    content=content,
                    is_file=False
                 )
                 msg_id = await database.execute(query)
                  # Broadcast to room
                 await manager.broadcast(conversation_id, {
                    "type": "text",
                    "id": msg_id,
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


    except WebSocketDisconnect:
         manager.disconnect(conversation_id, websocket)
         await manager.broadcast(conversation_id, {
            "type": "system",
            "content": f"{username} left the room",
            "timestamp": str(datetime.utcnow())
        })
