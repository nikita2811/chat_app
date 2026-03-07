from fastapi import APIRouter,Request,Depends
from .deps import get_user_service
from .service import UserService
from app.core.dependencies import get_current_user


user_router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@user_router.get("/me")
async def get_me(request: Request,service:UserService=Depends(get_user_service)):
    user_id = request.state.user_id
    return await service.get_user(user_id)

@user_router.get("/recommendations")
async def get_recommendations(current_user =Depends(get_current_user),service:UserService=Depends(get_user_service)):
    return service.recommendations(current_user)
