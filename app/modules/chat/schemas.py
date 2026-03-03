from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

class UserBasic(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

class Conversationrequest(BaseModel):
    group_name:Optional[str] = None
    user_ids:List[int]


class ConversationResponse(BaseModel):
    id: int
    group_name: Optional[str] = None
    type: str
    chat_count: int
    created_at: datetime
    participants: List[UserBasic] = []             # list of user ids

    class Config:
        orm_mode = True