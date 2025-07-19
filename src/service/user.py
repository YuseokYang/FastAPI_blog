from typing import Annotated
import bcrypt
from fastapi import Depends

from database.orm import User
from database.repository import UserRepository

class SignBase:
    encoding = "UTF-8"

    def hash_password(self, password: str) -> str:
        hashed_password = bcrypt.hashpw(password.encode(self.encoding), salt=bcrypt.gensalt())
        return hashed_password.decode(self.encoding)


class SignUpService(SignBase):
    async def check_duplicated_username(self, username, user_repo: UserRepository) -> bool:
        return await user_repo.get_user_by_username(username) is not None


class SignInService(SignBase):
    def verify_password(self, plain: str, user_password: str) -> bool:
        return bcrypt.checkpw(plain.encode(self.encoding), user_password.encode(self.encoding))
