from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CommentBase(BaseModel):
    content: str = "Hi!"


class CommentDB(CommentBase):
    id: int
    is_blocked: bool
    created_at: datetime
    post_id: int
    owner_id: int

    class Config:
        from_attributes = True


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class CommentRead(CommentUpdate):
    id: int
    post_id: int
    owner_id: int
    comment_id_reply_to: Optional[int]
