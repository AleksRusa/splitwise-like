from fastapi import Depends, APIRouter

from splitwise.schemas.user import UserCreate, UserOut
from splitwise.services.auth import register_new_user
from splitwise.database import get_db
from splitwise.logger import logger


router = APIRouter(prefix="/user", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def user_register(new_user: UserCreate, session=Depends(get_db)) -> str:
    result = await register_new_user(new_user, session)
    logger.info(f"user {result.email} successfully created")
    return result
