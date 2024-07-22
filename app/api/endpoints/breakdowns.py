from datetime import date
from starlette import status as st

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import current_active_user
from app.api.schemas import user_schemas, post_schemas
from app.db.database import get_async_session
from app.db.managers.comment_manager import CommentManager
from app.db.managers.post_manager import PostManager

breakdown = APIRouter(
    prefix="/api/breakdowns",
    tags=["daily breakdown"]
)


@breakdown.get(
    "/comments-daily-breakdown/user/me/", status_code=200,
    description="Get comments breakdown by user"
)
async def get_comments_daily_breakdown(
        date_from: date = date.min, date_to: date = date.today(),
        db: AsyncSession = Depends(get_async_session),
        user: user_schemas.UserRead = Depends(current_active_user)
):
    comment_manager = CommentManager(db)
    db_comments = await comment_manager.get_many(date_from=date_from, date_to=date_to, user_id=user.id)
    if db_comments:
        status_by_comments = comment_manager.format_comments_by_user(comments=db_comments, user_id=user.id)
        res = {
            status: comment_manager.filter_by_blocked(db_comments)
            for status, db_comments in status_by_comments.items()
        }
        return res
    else:
        raise HTTPException(status_code=st.HTTP_204_NO_CONTENT)


@breakdown.get(
    "/posts-daily-breakdown/user/me/", status_code=200,
    description="Get posts breakdown by user"
)
async def get_posts_daily_breakdown(
        date_from: date = date.min, date_to: date = date.today(),
        db: AsyncSession = Depends(get_async_session),
        user: user_schemas.UserRead = Depends(current_active_user)
):
    post_manager = PostManager(db)
    db_posts = await post_manager.get_many(date_from, date_to, user_id=user.id)
    return post_manager.filter_by_blocked(db_posts)

