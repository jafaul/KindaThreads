from datetime import datetime

from pydantic import BaseModel

from app.api.schemas.comment_schemas import CommentRead


class PostBase(BaseModel):
    content: str = "Hi!"


class PostPublic(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    comments: list["CommentRead"]


class PostCreate(PostBase):
    auto_reply: bool


class PostPrivate(PostPublic):
    auto_reply: bool


class PostDB(PostPrivate):
    id: int
    content: str = "Hi!"
    is_blocked: bool
    auto_reply: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostUpdate(PostCreate):
    pass
