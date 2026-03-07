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
from app.core.logger import setup_logger
from loguru import logger
from app.modules.chat.ws import router as chat_ws_router
import sys
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

setup_logger()


logger.info("app started")
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

app.add_middleware(SlowAPIMiddleware)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10/minute"]   # global limit
)
app.state.limiter = limiter

# handle rate limit exceeded error
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)



@app.get("/")
def root():
    return {"message": "FastAPI + PostgreSQL is running!"}


app.include_router(router)
app.add_middleware(AuthMiddleware)
app.include_router(chat_router)
app.include_router(user_router)
app.include_router(chat_ws_router)



