from datetime import timedelta

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"])


async def create_access_token(data: dict, expires_delta: timedelta) -> str:
    pass


async def decode_token(token: str):
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
