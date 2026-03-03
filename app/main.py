from fastapi import FastAPI
from app.modules.auth.api import router
from app.modules.chat.api import chat_router
from app.modules.user.api import user_router
from app.core.redis import init_redis,close_redis
from app.middleware.AuthMiddleware import AuthMiddleware
from app.core.database import engine,Base
from sqlalchemy.ext.asyncio import create_async_engine
from contextlib import asynccontextmanager
import os
from fastapi.staticfiles import StaticFiles



async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Mount uploads folder for serving files
    os.makedirs("uploads", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    await init_redis()  
    await create_tables()  # create tables on startup
    yield
    await close_redis()


app = FastAPI(title = "Chat App",lifespan=lifespan)



@app.get("/")
def root():
    return {"message": "FastAPI + PostgreSQL is running!"}


app.include_router(router)
app.add_middleware(AuthMiddleware)
app.include_router(chat_router)
app.include_router(user_router)



