from datetime import datetime
from typing import Type, Optional

from sqlalchemy import Select, select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.schemas import comment_schemas, user_schemas
from app.db.managers.base_manager import BaseManager, ModelType
from app.db.managers.post_manager import PostManager
from app.db.models.comment import Comment


class CommentManager(BaseManager[[comment_schemas.CommentCreate, comment_schemas.CommentUpdate], Comment]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    @property
    def model_class(self) -> Type[ModelType]:
        return Comment

    ''' create comment with auto reply '''
    async def create(
            self,
            entity_create: comment_schemas.CommentCreate,
            owner_id: int,
            **kwargs
    ) -> Comment:

        comment_id_reply_to = kwargs['comment_id_reply_to']
        post_id = kwargs['post_id']

        comment_id: int = await super().create(
            entity_create=entity_create,
            owner_id=owner_id,
            comment_id_reply_to=comment_id_reply_to,
            post_id=post_id
        )

        return await self.create_auto_reply(post_id, owner_id, comment_id, entity_create)

    async def create_auto_reply(self, post_id, owner_id: int, comment_id, entity_create) -> Comment:
        comment: Comment = await self.get_one(comment_id)

        post_manager = PostManager(self.db)
        post = await post_manager.get_one(post_id)

        if post.auto_reply and owner_id != post.owner_id and not comment.is_blocked:
            auto_reply_content = await self._c.generate_auto_reply(entity_create.content)
            if not auto_reply_content:
                print("No content to reply to")
                return comment

            await super().create(
                entity_create=comment_schemas.CommentCreate(content=auto_reply_content),
                post_id=post.id,
                comment_id_reply_to=comment.id,
                owner_id=post.owner_id
            )
        return comment

    async def get_one(self, id_: int, query: Optional[Select] = None) -> ModelType:
        query = select(self.model_class).where(
            self.model_class.id == id_
        )
        return await super().get_one(id_, query)

    async def get_many_by_entity_owner_id(
            self,  entity_owner_id: int, from_: datetime, till_: datetime, visible_blocked: bool = False
    ) -> list[Comment] | None:
        filters = [
            Comment.post_id == entity_owner_id,
            Comment.created_at >= from_,
            Comment.created_at <= till_,
            Comment.is_blocked == visible_blocked
        ]

        query = select(self.model_class).where(
                and_(*filters)
            ).order_by(self.model_class.created_at)

        comments = await self._get_many_by_query(query)
        return comments

    async def get_many(
            self, date_from: datetime.date, date_to: datetime.date, user_id: int
    ) -> list[Comment]:

        filters = [
            func.date(Comment.created_at) >= date_from,
            func.date(Comment.created_at) <= date_to,
            or_(
                Comment.owner_id == user_id,
                Comment.post.has(owner_id=user_id),
                Comment.parent_comment.has(owner_id=user_id)
            )
        ]

        query = select(self.model_class).options(
            joinedload(Comment.post),
            joinedload(Comment.parent_comment)
        ).where(
                and_(*filters)
            ).order_by(self.model_class.created_at)

        comments = await self._get_many_by_query(query)

        return comments

    @staticmethod
    def format_comments_by_user(comments: list[Comment], user_id: int) -> dict[str, list[Comment]]: # dict[str, dict[str, list[Comment]]]:
        sent_comments = [comment for comment in comments if comment.owner_id == user_id]
        received_comments = [
                comment for comment in comments
                if (
                       comment.post.owner_id == user_id and comment.owner_id != user_id
                   ) or comment.parent_comment and comment.parent_comment.owner_id == user_id
            ]

        return {
            "sent": sent_comments,
            "received": received_comments
        }

    async def check_access_to_content(
            self,
            current_user: user_schemas.UserRead,
            post_owner_user_id: int,
            **kwargs
    ) -> bool:

        comment_id: int = kwargs['comment_id']
        access_lvl: str = kwargs.get('access_lvl', "delete")

        if access_lvl == "delete" and current_user.id == post_owner_user_id:
            return True

        comment = await self.get_one(id_=comment_id)
        if comment.owner_id == current_user.id:
            return True

        return False
