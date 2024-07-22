import asyncio
import os

import uvicorn
from fastapi import FastAPI

from app.api.endpoints.auth import auth_router
from app.api.endpoints.breakdowns import breakdown
from app.api.endpoints.comments import comments_router
from app.api.endpoints.posts import users_router
from app.core.config import config

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(comments_router)
app.include_router(breakdown)


if __name__ == '__main__':
    uvicorn.run("main:app", port=config.PORT, host=config.HOST, reload=True)
