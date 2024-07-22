from fastapi import APIRouter, Depends

from app.api.schemas.user_schemas import UserCreate, UserRead
from app.auth.auth import auth_backend, current_active_user, fastapi_users
from app.db.models.user import User
from app.db.models.post import Post
from app.db.models.comment import Comment

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# sigh in
auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth']
)

# sigh up
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth']
)


# check current user
@auth_router.get("/authenticated-route", response_model=UserRead)
async def authenticated_route(user: User = Depends(current_active_user)):
    return user


