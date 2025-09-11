from fastapi import APIRouter, Depends
from splitwise.database import get_db
from splitwise.schemas.expense import ExpenseCreate
from splitwise.services.expense import create_expense


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/add_expense")
async def create_new_expense(expense: ExpenseCreate, session=Depends(get_db)):
    result = await create_expense(data=expense, session=session)
    return result
