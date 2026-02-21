from pydantic import BaseModel,EmailStr,field_validator,model_validator
from datetime import datetime,timedelta
from typing import Optional

class UserCreate(BaseModel):
    name:str
    email:EmailStr
    password:str
    is_active:bool
    is_verified:bool
    confirm_password:str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, confirm_password, info):
        password = info.data.get("password")
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        


class UserAuth(BaseModel):
    email:EmailStr
    password:str

class ForgotPassword(BaseModel):
    email: EmailStr


class Resetpassword(BaseModel):
    new_password:str
    confirm_password:str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

    
    
