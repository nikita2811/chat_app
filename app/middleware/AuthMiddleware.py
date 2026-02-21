from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.core.config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
       if request.url.path.startswith("/auth"):
           return await call_next(request)
       
       auth_header = request.header.get("Authorization")
       if not auth_header:
           raise HTTPException(status_code=401, detail="Missing token")
       
       try:
           token = auth_header.split()
           payload = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
           request.state.user_id = payload.get("sub")
       except JWTError:
           raise HTTPException(status_code=401, detail="Invalid token")

       return await call_next(request)
           

