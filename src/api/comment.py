from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from database.orm import User, Comment
from database.repository import CommentRepository, PostRepository
from schema.request import CreateCommentRequest
from schema.response import CommentResponse
from service.security import get_current_user

router = APIRouter(prefix="/comment")

@router.post("/{post_id}", response_model=CommentResponse, status_code=201)
async def create_comment(
        post_id: int,
        comment_data: CreateCommentRequest,
        post_repo: Annotated[PostRepository, Depends()],
        comment_repo: Annotated[CommentRepository, Depends()],
        current_user: Annotated[User, Depends(get_current_user)]
):

    post = await post_repo.get_post_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post Not Found")

    comment = Comment.create(
        post_id=post_id,
        content=comment_data.content,
        user_id=current_user.id,
    )
    comment = await comment_repo.create_comment(comment)

    return CommentResponse.from_orm(comment)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
        comment_id: int,
        comment_data: CreateCommentRequest,
        comment_repo: Annotated[CommentRepository, Depends()],
        current_user: Annotated[User, Depends(get_current_user)]
):
    comment = await comment_repo.get_comment_by_id(comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment Not Found")

    if comment.user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not Authorized to update this comment")

    comment.content = comment_data.content
    comment = await comment_repo.update_comment(comment)
    return CommentResponse.from_orm(comment)


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
        comment_id: int,
        comment_repo: Annotated[CommentRepository, Depends()],
        current_user: Annotated[User, Depends(get_current_user)]
):

    comment = await comment_repo.get_comment_by_id(comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment Not Found")

    if comment.user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await comment_repo.delete_comment(comment)
    return {"message": "Comment deleted successfully"}