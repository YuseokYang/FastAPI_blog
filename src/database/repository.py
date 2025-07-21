from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.connection import get_db
from database.orm import User, Post, Comment
from schema.request import CreatePostRequest


class UserRepository:

    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return await self.session.scalar(stmt)

    async def save_user(self, user:User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

class PostRepository:

    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_posts(self):
        stmt = (
            select(Post)
            .options(selectinload(Post.author))
            .order_by(desc(Post.is_pinned), desc(Post.id))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_post_by_id(self, post_id):
        stmt = select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_post(self, post:Post):
        self.session.add(post)
        await self.session.commit()
        stmt = select(Post).options(selectinload(Post.author)).where(Post.id==post.id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update_post(self, post_id, post_data: CreatePostRequest):

        post = await self.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post Not Found")

        post.title = post_data.title
        post.content = post_data.content

        self.session.add(post)
        await self.session.commit()
        stmt = select(Post).options(selectinload(Post.author)).where(Post.id==post.id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def save_post(self, post: Post):  # ✅ pinned 상태만 바꿀 때 사용
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)



    async def delete_post(self, post_id: int):
        post = await self.get_post_by_id(post_id)
        if post:
            await self.session.delete(post)
            await self.session.commit()


class CommentRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def create_comment(self,comment: Comment):
        self.session.add(comment)
        await self.session.commit()

        stmt = select(Comment).options(selectinload(Comment.user)).where(Comment.id==comment.id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_comment_by_comment_id(self, comment_id):
        stmt = select(Comment).options(selectinload(Comment.user)).where(Comment.id==comment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_comment(self, comment: Comment):
        self.session.add(comment)
        await self.session.commit()

        stmt = select(Comment).options(selectinload(Comment.user)).where(Comment.id==comment.id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_comment(self, comment: Comment):
        await self.session.delete(comment)
        await self.session.commit()
        return


    async def get_comments_by_post_id(self, post_id: int) -> list[Comment]:
        stmt = select(Comment).options(selectinload(Comment.user)).where(Comment.post_id == post_id).order_by(Comment.id.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())