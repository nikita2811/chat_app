from fastapi import APIRouter,Depends,BackgroundTasks,Request,Response,HTTPException
from .models import UserCreate,UserAuth,ForgotPassword,Resetpassword
from .service import AuthService
from .deps import get_auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register")
async def create_user(user:UserCreate,bg:BackgroundTasks,service:AuthService = Depends(get_auth_service)):
    return await service.create_user(user,bg)

@router.post("/login")
async def authenticate_user(data:UserAuth,response:Response,service:AuthService=Depends(get_auth_service)):
    return await service.authenticate_user(data,response)

@router.get("/verify-email")
async def verify_email(token:str,service:AuthService=Depends(get_auth_service)):
    return await service.verify_email(token)

@router.post("/resend-verify-email")
async def resend_verify_email(user:ForgotPassword,bg:BackgroundTasks,service:AuthService=Depends(get_auth_service)):
    return await service.resend_verify_email(user,bg)

@router.post("/forgot-password")
async def forgot_password(user:ForgotPassword,bg:BackgroundTasks,service:AuthService=Depends(get_auth_service)):
    return await service.forgot_password(user,bg)

@router.post("/reset-password")
async def reset_password(token:str,user_password:Resetpassword,service:AuthService=Depends(get_auth_service)):
    return await service.reset_password(token,user_password)

@router.post("/refresh")
async def refresh(request: Request, response: Response,service:AuthService=Depends(get_auth_service)):
    refresh_token = request.cookies.get("refresh_token")
    return await service.refresh(refresh_token,response)

@router.post("/logout")
async def logout(request: Request, response: Response,service:AuthService=Depends(get_auth_service)):
    refresh_token = request.cookies.get("refresh_token")
    print(refresh_token)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    return await service.delete_refresh_token(refresh_token,response)
    


