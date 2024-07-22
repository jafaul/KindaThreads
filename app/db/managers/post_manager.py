import datetime
from typing import Type, Optional

from sqlalchemy import select, and_, func, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.api.schemas import post_schemas, user_schemas
from app.db.managers.base_manager import BaseManager, ModelType
from app.db.models.post import Post


class PostManager(BaseManager[post_schemas.PostCreate, Post]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    @property
    def model_class(self) -> Type[ModelType]:
        return Post

    async def get_one(self, id_: int, query: Optional[Select] = None) -> Post:
        query = select(self.model_class).options(
            joinedload(Post.comments)
        ).where(
            and_(
                self.model_class.id == id_,
            )
        )
        return await super().get_one(id_, query)

    async def get_many_by_entity_owner_id(
            self,  entity_owner_id: int, from_: datetime, till_: datetime, visible_blocked=False
    ) -> list[Post] | None:
        filters = [
            Post.owner_id == entity_owner_id,
            Post.created_at >= from_,
            Post.created_at <= till_,
            Post.is_blocked == visible_blocked
        ]

        query = select(self.model_class).options(
            selectinload(Post.comments)).where(
                and_(*filters,)
            ).order_by(self.model_class.created_at.desc())

        posts = await self._get_many_by_query(query)
        return posts

    async def get_many(self, date_from: datetime.date, date_to: datetime.date, user_id: int) -> list[Post]:
        filters = [
            func.date(Post.created_at) >= date_from,
            func.date(Post.created_at) <= date_to,
        ]

        if user_id is not None:
            filters.append(Post.owner_id == user_id)

        query = select(self.model_class).where(
                and_(*filters,)
            ).order_by(self.model_class.created_at.desc())

        posts = await self._get_many_by_query(query)
        return posts

    async def check_access_to_content(
            self,
            current_user: user_schemas.UserRead,
            post_owner_user_id: int,
            **kwargs

    ) -> bool:
        if current_user.id == post_owner_user_id:
            return True
        else:
            return False
