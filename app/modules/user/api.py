from fastapi import APIRouter,Request,Depends
from .deps import get_user_service
from .service import UserService


user_router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@user_router.get("/me")
async def get_me(request: Request,service:UserService=Depends(get_user_service)):
    user_id = request.state.user_id
    return await service.get_user(user_id)
   
