from fastapi import APIRouter


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/add_expense")
async def create_new_expense():
    pass
