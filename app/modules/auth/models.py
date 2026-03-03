from sqlalchemy import Column, Integer, String,Boolean,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String,nullable=False)
    is_active = Column(Boolean,nullable=False,default=False)
    is_verified=Column(Boolean,nullable=False,default=False)
    interests=Column(ARRAY(String),default=list)
    verification_token=Column(String,nullable=True)
    token_expiry=Column(DateTime,nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reset_token = relationship("PasswordResetToken",back_populates="user",lazy="noload")
    conversation = relationship("Conversation",secondary="conversation_participants",back_populates="participants",lazy="noload")
    messages = relationship("Message",back_populates="sender",lazy="selectin")
    attachments = relationship("FileAttachment",back_populates="sender",lazy="selectin")

class PasswordResetToken(Base):
    __tablename__="password_reset_tokens"

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    token =Column(String,nullable=False)
    is_used = Column(Boolean, default=False)         # prevent reuse
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow())

    user = relationship("User",back_populates="reset_token",lazy="selectin")
    