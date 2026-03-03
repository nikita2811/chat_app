from fastapi import Request,Depends,HTTPException
from .database import get_db
from app.modules.auth.models import User
from sqlalchemy.future import select

async def get_current_user(request:Request,db=Depends(get_db)):
    user_id = getattr(request.state, "user_id", None)

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
   
    user_result = await db.execute(select(User).where(User.id == int(user_id)))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User is not verified")
    return user

    
