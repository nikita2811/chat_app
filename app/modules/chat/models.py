from app.core.database import Base
from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,Table,Enum
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from sqlalchemy.orm import relationship




conversation_participants = Table("conversation_participants",Base.metadata,
                                  Column("conversation_id", Integer, ForeignKey("conversations.id"), primary_key=True),
                                  Column("user_id", Integer, ForeignKey("users.id",ondelete="CASCADE"), primary_key=True))

class Conversation(Base):
    __tablename__ = "conversations"

    id=Column(Integer,primary_key=True,index=True)
    type = Column(Enum("private", "group",name="conversation_type"), nullable=False, default="private") 
    group_name=Column(String,nullable=True)
    chat_count = Column(Integer, default=0) 
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    participants = relationship("User",secondary="conversation_participants",
                                back_populates="conversation",
                                lazy="selectin",
                                passive_deletes=True )
    
    convo_messages=relationship("Message",back_populates="conversation",lazy="selectin")
    attachment= relationship("FileAttachment",back_populates="conversation",lazy="selectin")


    

class Message(Base):
    __tablename__ ="messages"
    id=Column(Integer,primary_key=True,index=True)
    content=Column(String,nullable=True)
    sender_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    conversation_id=Column(Integer,ForeignKey("conversations.id"),nullable=False)
    created_at=Column(DateTime(timezone=True),default=datetime.utcnow)

    file_attachment=relationship("FileAttachment",back_populates="messages",lazy="selectin")
    conversations=relationship("Conversation",back_populates="convo_messages",lazy="selectin")
    sender = relationship("User",back_populates="messages",lazy="selectin")


class FileAttachment(Base):
    __tablename__ = "file_attachments"
    id=Column(Integer,primary_key=True,index=True)
    sender_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    conversation_id=Column(Integer,ForeignKey("conversations.id"),nullable=False)
    message_id=Column(Integer,ForeignKey("messages.id"),nullable=False)
    file_name=Column(String,nullable=False)
    file_type = Column(String, nullable=True)           # image, video, document
    file_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    messages=relationship("Message",back_populates="file_attachment",lazy="selectin")
    conversation=relationship("Conversation",back_populates="attachment",lazy="selectin")
    sender = relationship("User",back_populates="attachment",lazy="selectin")
    
