from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, exists, and_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.managers.post_manager import PostManager
from app.db.models.comment import Comment
from app.db.models.post import Post
from app.db.models.user import User


def validate_start_date(start_date: datetime = datetime.min):
    if start_date > datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be in the future"
        )
    return start_date


async def user_existing_validation(db: AsyncSession, user_id: int):
    query = select(exists().where(and_(User.id == user_id)))
    result = await db.execute(query)
    user_exists = result.scalar()

    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )


async def post_validation(db: AsyncSession, post_id: int):
    query = select(exists().where(and_(Post.id == post_id)))
    result = await db.execute(query)
    post_exists = result.scalar()

    if not post_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post does not exist"
        )


async def post_by_user_validation(db: AsyncSession, post_id: int, user_id: int):
    query = select(exists().where(
        and_(
            Post.id == post_id,
            Post.owner_id == user_id
        )
    ))
    result = await db.execute(query)
    post_exists = result.scalar()

    if not post_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post does not exist for the given user"
        )


async def comment_existing_validation(db: AsyncSession, comment_id: int):
    query = select(exists().where(and_(Comment.id == comment_id)))
    result = await db.execute(query)
    comment_exists = result.scalar()

    if not comment_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment does not exist"
        )


def check_is_blocked(base):
    if base.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Content is blocked due to inappropriate content. "
                   f"You can unlock it by updating the content via id {base.id}",
            headers={"content-id": str(base.id)}
        )


async def check_is_blocked_post_by_id(db: AsyncSession, id_: int):
    pm = PostManager(db)
    post = await pm.get_one(id_)
    check_is_blocked(post)


async def check_access(access_allowed: bool):
    if not access_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this content is not allowed for your user id"
        )
