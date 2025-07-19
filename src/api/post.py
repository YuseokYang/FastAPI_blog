from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.orm import User, Post
from database.repository import PostRepository
from schema.request import CreatePostRequest
from schema.response import PostResponse
from service.security import get_current_user

router = APIRouter(prefix="/posts")


@router.get("/", response_model=list[PostResponse])
async def get_all_posts(
        post_repo: Annotated[PostRepository, Depends()]
):
    result = await post_repo.get_posts()
    return [PostResponse.from_orm(post) for post in result]


@router.post("/", response_model=PostResponse)
async def create_post(
        post_data: CreatePostRequest,
        post_repo: Annotated[PostRepository, Depends()],
        current_user: Annotated[User, Depends(get_current_user)]
):
    post = Post.create(post_data, user_id=current_user.id)

    post = await post_repo.create_post(post)

    return PostResponse.from_orm(post)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
        post_id:int,
        post_data: CreatePostRequest,
        post_repo: Annotated[PostRepository, Depends()],
        current_user: Annotated[User, Depends(get_current_user)],
):
    existing_post = await post_repo.get_post_by_id(post_id)
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post Not Found")

    if existing_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not Authorized")

    updated_post = await post_repo.update_post(post_id, post_data)
    return PostResponse.from_orm(updated_post)


@router.delete("/{post_id}", status_code=204)
async def delete_post(
        post_id: int,
        post_repo: Annotated[PostRepository, Depends()],
        current_user: Annotated[User, Depends(get_current_user)]
):
    post = await post_repo.get_post_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post Not Found")
    if current_user.id != post.user_id:
        raise HTTPException(status_code=403, detail="Not Authorized")

    await post_repo.delete_post(post_id)

    return {"message": "Post deleted successfully"}


@router.get("/{post_id}", response_model=PostResponse)
async def get_post_by_id(
        post_id: int,
        post_repo: Annotated[PostRepository,Depends()]
):
    post = await post_repo.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post Not Found")
    return PostResponse.from_orm(post)



