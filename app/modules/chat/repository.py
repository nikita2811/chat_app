from app.modules.auth.models import User
from sqlalchemy.future import select
from fastapi import HTTPException
from .models import Conversation,conversation_participants,Message,FileAttachment



class ChatRepository:
    def __init__(self,db):
        self.db = db
    

    async def create_conversation(self,data):
      group_name = data.group_name
      user_ids = data.user_ids

      result = await self.db.execute(select(User).where(User.id.in_(user_ids)))
      users = result.scalars().all()

      if len(users) != len(user_ids):
         raise HTTPException(status_code=400,detail="one or more user not found")
      
      conv_type = "group" if len(user_ids) > 2 else "private"

      if conv_type == "private":
         existing = await self.get_private_conversation(user_ids[0], user_ids[1])
         if existing:
            return existing
         
         # create conversation
         conversation = Conversation(
            group_name = group_name if conv_type == 'group' else None,
            type = conv_type,
            chat_count = 0
         )
         conversation.participants = list(users)
         self.db.add(conversation)
         await self.db.commit()
         await self.db.refresh(conversation)
         return conversation
      
    async def get_private_conversation(self,user_id1,user_id2):
       existing_conversation = await self.db.execute(select(Conversation).join(conversation_participants)
                                                     .where(conversation_participants.c.user_id == user_id1,
                                                            Conversation.type == "private"))
       conversations = existing_conversation.scalars().all()

       for conv in conversations:
           participant_ids = [p.id for p in conv.participants]
           if user_id2 in participant_ids:
                return conv
       return None
    
    async def get_conversation(self,current_user):
       result = await self.db.execute(select(Conversation).join(conversation_participants).where(conversation_participants.c.user_id == current_user))
       conversation = result.scalars().all()
       return conversation
    
    async def conversation_by_id(self,current_user,conversation_id):
        result = await self.db.execute(select(Conversation).join(conversation_participants).where(Conversation.id ==conversation_id,conversation_participants.c.user_id ==current_user))
        return result.scalar_one_or_none()
    
    async def add_participants(self,conversation_id,user_id):
       user_result = await self.db.execute(select(User).where(User.id == user_id))
       user = user_result.scalar_one_or_none()
       if not user:
          raise HTTPException(status_code=400,detail="User not found")
       conversation = await self.conversation_by_id(conversation_id)
       if not conversation:
          raise HTTPException(status_code=400,detail="Conversation not found")
       
       
       participant_ids = [p.id for p in conversation.participants]
       if user_id not in participant_ids:
          raise HTTPException(status_code=400,detail="User is already in conversation")
       conversation.participants.append(user)
       await self.db.commit()
       await self.db.refresh(conversation)
       return conversation
    
    async def remove_participants(self,conversation_id,user_id):
       user_result = await self.db.execute(select(User).where(User.id == user_id))
       user = user_result.scalar_one_or_none()
       if not user:
          raise HTTPException(status_code=400,detail="User not found")
       conversation = await self.conversation_by_id(conversation_id)
       participant_ids = [p.id for p in conversation.participants]
       if user_id not in participant_ids:
          raise HTTPException(status_code=400,detail="User is already in conversation")
       conversation.participants.remove(user)
       await self.db.commit()
       await self.db.refresh(conversation)
       return conversation
    
    async def delete_conversation(self,conversation_id,user_id):
       conversation = await self.conversation_by_id(conversation_id)
       if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
       
         
       participant_ids = [p.id for p in conversation.participants]
       if user_id not in participant_ids:
        raise HTTPException(status_code=403, detail="Not allowed to delete this conversation")

   
       await self.db.delete(conversation)
       await self.db.commit()
       return {"message": "Conversation deleted successfully"}
    
    async def get_messages(self,conversation_id,page,limit):
       offset = (page -1)*limit
       messages = await self.db.execute(select(Message)
                                        .where(Message.conversation_id == conversation_id)
                                        .order_by(messages.c.created_at)
                                        .limit(limit)
                                        .offset(offset))
       
       return {
          "message":messages
       }
    
    async def upload_file(self,conversation_id,current_user,results,file_urls):
      message = Message(
         sender_id=current_user.id,
         conversation_id=conversation_id,
         content = None
      )
      self.db.add(message)
      await self.db.commit()              # save to DB
      await self.db.refresh(message)

      for file in results:

       file_attachment=FileAttachment(
         sender_id=current_user.id,
         conversation_id=conversation_id,
         message_id=message.id,
         file_name=file
         file_type =           # image, video, ocument
         file_url =
         created_at =

      )

       
       
    
         
 
      
