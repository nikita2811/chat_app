from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.core.config import settings
from starlette.responses import JSONResponse

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
       if request.url.path.startswith("/auth/")or request.url.path == "/auth":
           return await call_next(request)
       
       auth_header = request.headers.get("Authorization")
       
       if not auth_header:
           return JSONResponse(status_code=401, content={"detail": "Missing token"})
          
       
       try:
           if not auth_header.startswith("Bearer "):
             return JSONResponse(status_code=401, content={"detail": "Invalid token format"})
           token = auth_header.split()
           payload = jwt.decode(token[1],settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
           user_id = payload.get("sub")
           if not user_id:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid token payload"}
                )

           request.state.user_id = user_id
       except JWTError:
          return JSONResponse(status_code=401, content={"detail": "Invalid token"})

       return await call_next(request)
           

