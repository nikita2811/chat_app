from fastapi import FastAPI
from app.modules.auth.api import router
from app.modules.chat.api import chat_router
from app.modules.user.api import user_router
from app.core.redis import init_redis,close_redis
from app.core.database import connect_to_mongo,close_mongo_connection
from fastapi.middleware import Middleware
from app.middleware.AuthMiddleware import AuthMiddleware



app = FastAPI(title = "Chat App",middleware=[
        Middleware(AuthMiddleware)
    ])

@app.on_event("startup")
async def startup():
    connect_to_mongo()
    await init_redis()

@app.on_event("shutdown")
async def shutdown():
    close_mongo_connection()
    await close_redis()



app.include_router(router)
app.include_router(chat_router)
app.include_router(user_router)



