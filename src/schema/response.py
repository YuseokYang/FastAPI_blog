from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict, EmailStr

from database.orm import Post, Comment


class SignUpResponse(BaseModel):
    id: Annotated[int, Field()]
    username: Annotated[str, Field()]
    email: Annotated[EmailStr | None, Field()]

    model_config = ConfigDict(from_attributes=True)


class SignInResponse(BaseModel):
    token: str


class PostResponse(BaseModel):
    id: int
    username: str
    title: str
    content: str
    is_pinned: bool  # ✅ 추가

    @classmethod
    def from_orm(cls, post: Post):
        return cls(
            id=post.id,
            title=post.title,
            content=post.content,
            username=post.author.username,
            is_pinned=post.is_pinned,  # ✅ 추가
        )

    model_config = ConfigDict(from_attributes=True)


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int
    username: str

    @classmethod
    def from_orm(cls, comment: Comment):
        return cls(
            id=comment.id,
            content=comment.content,
            user_id=comment.user_id,
            post_id=comment.post_id,
            username=comment.user.username
        )

    model_config = ConfigDict(from_attributes=True)