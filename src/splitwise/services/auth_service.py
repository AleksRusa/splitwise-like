from pydantic import EmailStr

from splitwise.schemas.user import Token, UserOut
from .user import select_user_by_email


async def login_for_access_token(email: EmailStr, password: str) -> Token:
    user: UserOut = validate_user(email, password)


async def validate_user(email: EmailStr, password: str) -> UserOut:
    user: UserOut = select_user_by_email(email)
