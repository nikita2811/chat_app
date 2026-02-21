from app.core.security import token_expiry,create_access_token,generate_token,hash_token,create_refresh_token
from datetime import datetime,timedelta
from app.core.password import hash_password,verify_password
from jose import jwt,JWTError,ExpiredSignatureError
from app.core.config import settings
from fastapi import HTTPException,Response
from app.core import redis as redis_module
class AuthService:
    def __init__(self,repo):
        self.repo = repo

    async def create_user(self,user,bg):
       
        user_data = user.model_dump(exclude={"confirm_password"})
        user_data["password"]=hash_password(user_data["password"])
        user_data["created_at"]=datetime.utcnow()
        user_data["verification_token"] = generate_token()
        user_data["token_expiry"]=token_expiry()

        return await self.repo.create_user(user_data,bg)
    
    async def verify_email(self,token):
        return await self.repo.verify_email(token)
    
    async def resend_verify_email(self,user,bg):
        user_data = user.model_dump()
        return await self.repo.resend_verify_email(user_data,bg)

    async def authenticate_user(self,data,response):
        user_data= data.model_dump()
        user = await self.repo.authenticate_user(user_data)
        
        if not user:
            raise ValueError("user does not exists")
        if not verify_password(user_data["password"],user["password"]):
            raise ValueError("Invalid Credentials")
        
        token = create_access_token({"sub":str(user["_id"])})
        refresh_token = create_refresh_token({"sub":str(user["_id"])})
        token_hash=hash_token(refresh_token)
       
        #refresh_token = await self.repo.save_refresh_token(str(user["_id"]))
        await redis_module.redis_client.setex(
        f"refresh:{token_hash}",
        7 * 24 * 60 * 60,
        str(user["_id"])
    )
        response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,          # HTTPS only
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
        return {
            "access_token":token,
             "token_type": "bearer"
        }
    
    async def forgot_password(self,user,bg):
        user_data = user.model_dump()
        return await self.repo.forgot_password(user_data,bg)
    
    async def reset_password(self,token,user_password):
        user_data = user_password.model_dump(exclude={"confirm_password"})
        try:
            payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
            email = payload.get("sub")
            
             
        except JWTError:
         raise HTTPException(status_code=400,detail="Invalid or expired token")
        user_data["new_password"]=hash_password(user_data["new_password"])
        return await self.repo.reset_password(email,user_data)
    
    async def refresh(self,refresh_token,response):
         token_hash = hash_token(refresh_token)
         
         user_id = await redis_module.redis_client.get(f"refresh:{token_hash}")
        
         if not user_id:
           raise HTTPException(401, "Session expired")
#  ROTATION
         await redis_module.redis_client.delete(f"refresh:{token_hash}")

         new_refresh = create_refresh_token({"sub": user_id})
         new_hash = hash_token(new_refresh)

         await redis_module.redis_client.setex(
        f"refresh:{new_hash}",
        7 * 24 * 60 * 60,
        user_id
    )  
         new_access = create_access_token({"sub": user_id})

         response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/"
    )

         return {"access_token": new_access,"type":"bearer"}
        

         
    
    async def delete_refresh_token(self,refresh_token,response):
        if refresh_token:
         await redis_module.redis_client.delete(f"refresh:{hash_token(refresh_token)}")

        response.delete_cookie("refresh_token", path="/auth/refresh")
        return {"message": "Logged out"}
      
        

