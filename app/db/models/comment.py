from typing import TYPE_CHECKING

from app.db.database import Base

from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime


if TYPE_CHECKING:
    from .post import Post
    from .user import User


class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(String(255))
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("post.id"))
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    comment_id_reply_to: Mapped[int] = mapped_column(Integer, ForeignKey("comment.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    parent_comment: Mapped["Comment"] = relationship(
        "Comment", remote_side=[id], back_populates="replies")

    replies: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="parent_comment", cascade="all, delete-orphan")

    owner: Mapped["User"] = relationship("User", back_populates="comments")

