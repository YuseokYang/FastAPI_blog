from typing import Annotated

from pydantic import BaseModel, Field, EmailStr


class SignUpRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=30, description="3자 이상 사용자 이름")]
    password: Annotated[str, Field(min_length=4, max_length=128, description="4자 이상 비밀번호")]
    email: Annotated[EmailStr | None, Field(description="이메일 (선택)")] = None


class SignInRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=30, description="3자 이상 사용자 이름")]
    password: Annotated[str, Field(min_length=4, max_length=128, description="4자 이상 비밀번호")]


class CreatePostRequest(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=200, description="제목은 한 글자 이상")]
    content: Annotated[str, Field(min_length=1)]


class CreateCommentRequest(BaseModel):
    content: str
