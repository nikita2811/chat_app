from bson import ObjectId
from app.core.email import fm
from fastapi_mail import MessageSchema
from app.core.security import create_refresh_token,create_reset_token,hash_token
from datetime import datetime,timedelta
from fastapi import HTTPException
from app.core.config import settings


class AuthRepository:
    def __init__(self,db):
        self.collection = db.users
        self.token_collection = db.refresh_token
        self.password_reset = db.password_reset

    
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
      
        exists = await self.collection.find_one(
                 {"email": user["email"]},
                 {"_id": 1}
                )
        
        if exists is not None:
            return {
                "message": "email already exists"
            }
        
        data = await self.collection.insert_one(user)
        id = ObjectId(data.inserted_id)
        bg.add_task(self.send_verification_email, user["email"],user["verification_token"])
        return {
            "_id":str(id),
            "message":"user created successfully"
        }
    
    async def verify_email(self,token):
        user = await self.collection.find_one({
            "verification_token":token,
            "token_expiry":{"$gt":datetime.utcnow()}
        })
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        await self.collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"is_verified": True},
            "$unset": {"verification_token": "", "token_expiry": ""}
        }
       )

        return {"message": "Email verified successfully"}
    

    async def resend_verify_email(self,user,bg):
        user = await self.collection.find_one({
            "email":user["email"],
            "is_verified":False
        })
        if not user:
            raise HTTPException(status_code=400, detail="User not found Or Already Verified")
        bg.add_task(self.send_verification_email, user["email"],user["verification_token"])
        return {
            "message":"email sent successfully"
        }

    async def authenticate_user(self,data):
        user = await self.collection.find_one({"email":data["email"]})
        return user
    
    async def save_refresh_token(self,user_id):
        
        exists = await self.token_collection.find_one({"_id":ObjectId(user_id)})
        if not exists:
            token = create_refresh_token({"sub": user_id})
            hashed_token = hash_token(token)
            await self.token_collection.insert_one({
            "user_id":user_id,
            "refresh_token":hashed_token,
            "expires_at":datetime.utcnow()+timedelta(settings.REFRESH_EXPIRE_DAYS)
        })
        
        return token
    

    async def forgot_password(self,user_data,bg):
        user = await self.collection.find_one({"email":user_data["email"]})
        if not user:
            raise HTTPException(status=400,detail="email not found")
        token = create_reset_token(user["email"])
        hashed_token = hash_token(token)
       
        
        await self.password_reset.insert_one({
            "user_id":user["_id"],
            "email":user["email"],
            "token":hashed_token,
            "expires_at":datetime.utcnow()+timedelta(hours=1),
            "used":False
        })
        bg.add_task(self.send_forgot_password_email,user["email"],token)
        return {
            "message":"link sent successfully"
        }
    

    async def reset_password(self,email,user_data): 
        password = user_data["new_password"]
        user = await self.collection.find_one({"email":email})
        if not user:
            raise HTTPException(status_code=400,detail="Invalid or expired token")
        await self.collection.update_one(
                 {"email":email},
                 {"$set":{
                     "password":password
                 }}
                )

        await self.password_reset.update_one(
               {"email":email},
               {"$set":{"used":True}}
             )
        return {
                 "messsage":"password updated successfully"
             }
    
    async def get_refresh_token(self,user_id,token_hash):
        print(token_hash)
        data = await self.token_collection.find_one({"refresh_token":token_hash,"user_id":user_id})
        return data
    
    async def delete_refresh_token(self,token_hash,user_id):
        await self.token_collection.delete_one({"refresh_token":token_hash,"user_id":user_id})
        return {
            "message":"token deleted successfully"
        }
        
         
         

        
     
         

        
    