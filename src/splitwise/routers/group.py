from fastapi import APIRouter, Depends
from splitwise.database import get_db
from splitwise.routers.auth import get_current_user_from_token


router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/create_new")
async def create_new_group(
    session=Depends(get_db),
    user_id=Depends(get_current_user_from_token),
) -> str:
    pass
