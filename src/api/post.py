import os
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.orm import User, Post
from database.repository import PostRepository
from schema.request import CreatePostRequest
from schema.response import PostResponse
from service.file import upload_file
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


@router.patch("/{post_id}/pin")
async def pin_post(
        post_id: int,
        is_pinned: Annotated[bool, Body(..., embed=True)],
        post_repo: Annotated[PostRepository, Depends()],
        current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.admin:
        raise HTTPException(status_code=403, detail="관리자만 공지글을 설정할 수 있습니다.")

    post = await post_repo.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post Not Found")

    post.pinned() if is_pinned else post.unpinned()
    await post_repo.save_post(post)
    return {"message": "공지글 상태가 변경되었습니다."}





@router.post("/upload/image")
async def upload_image(
    file: Annotated[UploadFile, File(...)],
    request: Request  # 👉 요청 정보 포함
):
    url_data = await upload_file(file)

    # "url": "/static/uploads/xxx.jpg" 형식으로 리턴된 값을 절대 URL로 변경
    relative_url = url_data["url"]
    base_url = str(request.base_url).rstrip("/")  # 예: http://localhost:8000
    absolute_url = f"{base_url}{relative_url}"

    return {"url": absolute_url}



