from pydantic import EmailStr

from splitwise.models.user import User


async def select_user_by_email(email: EmailStr) -> User:
    pass
