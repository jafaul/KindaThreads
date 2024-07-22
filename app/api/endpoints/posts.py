from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.schemas import post_schemas, user_schemas
from app.api.validation_tools import validate_start_date, user_existing_validation, post_validation, \
    post_by_user_validation, check_is_blocked, check_access
from app.db.database import get_async_session
from app.auth.auth import current_active_user
from app.db.managers.post_manager import PostManager

users_router = APIRouter(
    tags=["posts"]
)

# todo change repo, make it visible for everyone
# todo write tests

# todo make instructions or project running with readme


@users_router.get(
    "/users/{user_id}/posts/",
    response_model=list[post_schemas.PostDB],
    status_code=status.HTTP_200_OK,
    description="Getting posts excluding blocked posts"
)
async def get_posts(
        user_id: int,
        user: user_schemas.UserRead = Depends(current_active_user),
        start_date: datetime = Depends(validate_start_date),
        end_date: datetime = datetime.now(),
        db: AsyncSession = Depends(get_async_session),
):
    await user_existing_validation(db, user_id)

    post_manager = PostManager(db=db)
    posts = await post_manager.get_many_by_entity_owner_id(
        from_=start_date, till_=end_date, entity_owner_id=user_id
    )
    if not posts:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No posts found.")
    return posts


@users_router.get(
    "/users/{user_id}/posts/{post_id}", status_code=status.HTTP_200_OK,
    description="Getting a specific published post by id with all comments"
)
async def get_post(
        post_id: int,
        user_id: int,
        user: user_schemas.UserRead = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):

    await post_validation(db, post_id)
    await user_existing_validation(db, user_id)
    await post_by_user_validation(db, post_id, user_id)

    post_manager = PostManager(db=db)
    post_db = await post_manager.get_one(id_=post_id)

    if post_db.is_blocked and post_db.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this post is blocked",
            headers={"X-Error": "PostBlocked"}
        )
    elif not post_db.is_blocked and post_db.owner_id != user.id:
        return post_schemas.PostPublic(
            id=post_id, created_at=post_db.created_at, updated_at=post_db.updated_at, content=post_db.content)
    else:
        return post_db


@users_router.post("/users/{user_id}/posts/", response_model=post_schemas.PostDB, status_code=status.HTTP_201_CREATED)
async def create_post(
        user_id: int,
        post_create: post_schemas.PostCreate,
        user: user_schemas.UserRead = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    post_manager = PostManager(db=db)
    await check_access(
        await post_manager.check_access_to_content(current_user=user, post_owner_user_id=user_id)
    )
    post_id = await post_manager.create(entity_create=post_create, owner_id=user.id)
    post = await post_manager.get_one(post_id)
    check_is_blocked(post)
    return post


@users_router.put(
    "/users/{user_id}/posts/{post_id}", response_model=post_schemas.PostDB, status_code=status.HTTP_202_ACCEPTED
)
async def update_post(
        post_id: int,
        user_id: int,
        post_update: post_schemas.PostUpdate,
        user: user_schemas.UserRead = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    await post_validation(db, post_id)

    post_manager = PostManager(db=db)
    await check_access(await post_manager.check_access_to_content(
        current_user=user, post_owner_user_id=user_id
        )
    )

    await post_manager.update(post_id, post_update)
    post_db = await post_manager.get_one(post_id)
    check_is_blocked(post_db)
    return post_db


@users_router.delete("/users/{user_id}/posts/{post_id}", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def del_post(
        post_id: int,
        user_id: int,
        user: user_schemas.UserRead = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    await post_validation(db, post_id)
    await user_existing_validation(db, user_id)
    await post_by_user_validation(db, post_id, user_id)

    post_manager = PostManager(db=db)

    await check_access(
        await post_manager.check_access_to_content(
            current_user=user, post_owner_user_id=user_id
        )
    )

    await post_manager.delete(post_id)

    return {"message": f"Post with id {post_id} has been deleted successfully."}

