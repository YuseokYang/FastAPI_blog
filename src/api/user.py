from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.orm import User
from database.repository import UserRepository
from schema.request import SignUpRequest, SignInRequest
from schema.response import SignUpResponse, SignInResponse
from service.security import create_JWT
from service.user import SignUpService, SignInService

router = APIRouter(prefix="/user")


@router.post("/sign-up")
async def user_sign_up(
        request: SignUpRequest,
        user_service: Annotated[SignUpService, Depends()],
        db: Annotated[AsyncSession, Depends(get_db)]

):
    user_repo = UserRepository(db)
    # username이 중복인지 확인
    if await user_service.check_duplicated_username(request.username, user_repo):
        raise HTTPException(status_code=400, detail="이미 해당 id가 존재합니다.")
    hashed_password = user_service.hash_password(request.password)

    user = User.create(
        username=request.username,
        hashed_password=hashed_password,
        email = request.email
    )

    user = await user_repo.save_user(user)
    return SignUpResponse.model_validate(user)


@router.post("/sign-in")
async def user_sign_in(
        request: SignInRequest,
        db: Annotated[AsyncSession, Depends(get_db)],
        user_service: Annotated[SignInService, Depends()]
):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(request.username)
    if (user is None) or (not user_service.verify_password(request.password, user.hashed_password)):
        raise HTTPException(status_code=401, detail="Not Authorized")

    token = create_JWT(request.username, user.admin)
    return SignInResponse(token=token)
