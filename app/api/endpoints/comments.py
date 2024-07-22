from datetime import datetime

from fastapi import APIRouter, Query, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth.auth import current_active_user
from app.api.schemas import comment_schemas, user_schemas
from app.api.validation_tools import post_validation, check_is_blocked, post_by_user_validation, \
    user_existing_validation, comment_existing_validation, validate_start_date, check_is_blocked_post_by_id, \
    check_access
from app.db.database import get_async_session
from app.db.managers.comment_manager import CommentManager


comments_router = APIRouter(
    tags=["comments"],
)


@comments_router.post(
    "/users/{user_id}/posts/{post_id}/comments/",
    response_model=comment_schemas.CommentRead,
    status_code=status.HTTP_201_CREATED
)
async def create_comment(
        post_id: int,
        comment: comment_schemas.CommentCreate,
        user_id: int,
        comment_id: int | None = Query(
            description="comment_id to which we respond", default=None),
        user: user_schemas.UserRead = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    await post_validation(db, post_id)
    await user_existing_validation(db, user_id)
    await post_by_user_validation(db, post_id, user_id)
    await check_is_blocked_post_by_id(db, post_id)
    if comment_id is not None:
        await comment_existing_validation(db, comment_id)

    comment_controller = CommentManager(db=db)
    comment = await comment_controller.create(
        entity_create=comment, owner_id=user.id, comment_id_reply_to=comment_id, post_id=post_id)

    check_is_blocked(comment)

    return comment_schemas.CommentRead(
        id=comment.id,
        post_id=comment.post_id,
        content=comment.content,
        owner_id=comment.owner_id,
        is_blocked=comment.is_blocked,
        updated_at=comment.updated_at,
        comment_id_reply_to=comment.comment_id_reply_to,
    )


@comments_router.get(
    "/users/{user_id}/posts/{post_id}/comments/{comment_id}",
    description="getting comment and all replies", response_model=comment_schemas.CommentDB,
)
async def get_comment(
        user_id: int,
        post_id: int,
        comment_id: int | None = Path(description="comment_id to which comment we want to read"),
        user: user_schemas.UserRead = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session),
):

    await post_validation(db, post_id)
    await user_existing_validation(db, user_id)
    await post_by_user_validation(db, post_id, user_id)
    await comment_existing_validation(db, comment_id)

    comment_controller = CommentManager(db=db)
    comment = await comment_controller.get_one(comment_id)
    return comment


@comments_router.get(
    "/users/{user_id}/posts/{post_id}/comments/",
    response_model=list[comment_schemas.CommentRead],
    description="getting all comments for current post"
)
async def get_published_comments_by_post(
        user_id: int,
        post_id: int,
        user: user_schemas.UserRead = Depends(current_active_user),
        start_date: datetime = Depends(validate_start_date),
        end_date: datetime = datetime.now(),
        db: AsyncSession = Depends(get_async_session)
):
    await post_validation(db, post_id)
    await user_existing_validation(db, user_id)
    await post_by_user_validation(db, post_id, user_id)

    comment_controller = CommentManager(db=db)
    comments = await comment_controller.get_many_by_entity_owner_id(
        entity_owner_id=post_id, from_=start_date, till_=end_date)
    if comments:
        return [comment_schemas.CommentRead(
            id=comment.id,
            post_id=comment.post_id,
            owner_id=comment.owner_id,
            comment_id_reply_to=comment.comment_id_reply_to,
            updated_at=comment.updated_at,
            content=comment.content
        ) for comment in comments]
    else:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT
        )


@comments_router.put(
    "/users/{user_id}/posts/{post_id}/comments/{comment_id}", response_model=comment_schemas.CommentRead, status_code=status.HTTP_202_ACCEPTED
)
async def update_comment(
        post_id: int,
        user_id: int,
        comment_id: int,
        comment_update: comment_schemas.CommentUpdate,
        user: user_schemas.UserRead = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    await post_validation(db, post_id)
    await user_existing_validation(db, user_id)
    await post_by_user_validation(db, post_id, user_id)
    await comment_existing_validation(db, comment_id)

    comment_manager = CommentManager(db=db)
    await check_access(
        await comment_manager.check_access_to_content(
            current_user=user, post_owner_user_id=user_id,
            comment_id=comment_id, access_lvl="update"
        )
    )

    await comment_manager.update(comment_id, comment_update)
    comment = await comment_manager.get_one(comment_id)
    check_is_blocked(comment)

    await comment_manager.create_auto_reply(post_id, user.id, comment_id, comment_update)

    return comment_schemas.CommentRead(
        id=comment.id,
        post_id=comment.post_id,
        content=comment.content,
        owner_id=comment.owner_id,
        is_blocked=comment.is_blocked,
        updated_at=comment.updated_at,
        comment_id_reply_to=comment.comment_id_reply_to
    )


@comments_router.delete("/users/{user_id}/posts/{post_id}/comments/{comment_id}", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def del_comment(
        comment_id: int,
        user_id: int,
        post_id: int,
        user: user_schemas.UserRead = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    await post_validation(db, post_id)
    await user_existing_validation(db, user_id)
    await post_by_user_validation(db, post_id, user_id)
    await comment_existing_validation(db, comment_id)

    comment_manager = CommentManager(db=db)
    await check_access(
        await comment_manager.check_access_to_content(
            current_user=user, post_owner_user_id=user_id,
            comment_id=comment_id, access_lvl="delete"
        )
    )

    await comment_manager.delete(comment_id)
    return {"msg": f"Comment with id {comment_id} deleted successfully"}


