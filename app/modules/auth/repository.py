from bson import ObjectId
from app.core.email import fm
from fastapi_mail import MessageSchema
from app.core.security import create_refresh_token,create_reset_token,hash_token
from datetime import datetime,timedelta,timezone
from fastapi import HTTPException
from app.core.config import settings
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from .models import User,PasswordResetToken
from sqlalchemy import update 


class AuthRepository:
    def __init__(self,db):
        self.db = db
        

    
    async def send_verification_email(self,email,token):
        verification_link=f"http://localhost:8000/auth/verify-email?token={token}"
        message=MessageSchema(
            subject="verify your email",
            recipients=[email],
            template_body={
            "verification_link": verification_link
            },
          subtype="html"
        )
        
        await fm.send_message(message, template_name="verify_email.html")
     
    
    async def send_forgot_password_email(self,email,token):
        reset_link = f"http://localhost:8000/auth/reset-password?token={token}"
        message =MessageSchema(
            subject= "Reset Password",
            recipients=[email],
            template_body={
                "reset_link":reset_link
            },
            subtype="html"

        )
        await fm.send_message(message,template_name="reset_password.html")

    async def create_user(self,user,bg):
        result = await  self.db.execute(select(User.id).where(User.email == user["email"]))
        exists = result.scalar_one_or_none()
         # Check if exists
        if exists:
          raise HTTPException(status_code=400, detail="Email already registered")
      
         # Create new user
        new_user = User(**user)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        bg.add_task(self.send_verification_email, user["email"],user["verification_token"])
        return new_user
       
    
    async def verify_email(self,token):
        result = await self.db.execute(select(User).where(User.verification_token == token,User.token_expiry > datetime.utcnow()))
        user = result.scalar_one_or_none()
        
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        user.verification_token = None
        user.token_expiry = None
        user.is_verified = True
        await self.db.commit()
        await self.db.refresh(user)
        
        return {"message": "Email verified successfully"}
    

    async def resend_verify_email(self,user,bg):
        result = await self.db.execute(select(User).where(User.email == user["email"],User.is_verified.is_(False)))
        user_exist = result.scalar_one_or_none()
        if not user_exist:
            raise HTTPException(status_code=400, detail="User not found Or Already Verified")
        bg.add_task(self.send_verification_email, user_exist.email,user_exist.verification_token)
        return {
            "message":"email sent successfully"
        }

    async def authenticate_user(self,data):
        result = await self.db.execute(select(User).where(User.email == data["email"]))
        user = result.scalar_one_or_none(
            
        )
        return user
        
    async def forgot_password(self,user_data,bg):
        result = await self.db.execute(select(User).where(User.email==user_data.email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status=400,detail="email not found")
        token = create_reset_token(user.email)
        hashed_token = hash_token(token)
        
        await self.db.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.user_id == user.id)
            .values(is_used=True)
        )
        reset_token =PasswordResetToken(
            user_id=user.id,
            token=hashed_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            is_used=False
        )

        self.db.add(reset_token)
        await self.db.commit()
        await self.db.refresh(reset_token)
       
        bg.add_task(self.send_forgot_password_email,user.email,token)
        return {
            "message":"link sent successfully"
        }
    

    async def reset_password(self,email,user_data): 
        password = user_data["new_password"]
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
       
        if not user:
            raise HTTPException(status_code=400,detail="Invalid or expired token")
        user.password = password
        
       
        await self.db.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.user_id == user.id)
            .values(is_used=True)
        )
        await self.db.commit()
        await self.db.refresh(user)

       
        return {
                 "messsage":"password updated successfully"
             }
    
   
         
         

        
     
         

        
    