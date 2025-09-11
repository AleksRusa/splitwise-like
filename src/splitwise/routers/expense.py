from fastapi import APIRouter, Depends
from splitwise.database import get_db
from splitwise.routers.auth import get_current_user_from_token
from splitwise.schemas.expense import ExpenseCreate, ExpenseDTO
from splitwise.services.expense import create_expense, select_all_group_expenses
from splitwise.utils.decorators import (
    validate_user_membership_in_group,
    validate_user_permissions_for_group_id,
)


router = APIRouter(prefix="/expenses", tags=["expenses"])


"""
    @post("add_expense")
    получаем данные о расходе + между кем делить расход ✅
    проверяется есть ли пользователь в этой группе, то есть может ли он добавлять в ней расходы ✅
    есть ли пользователи указанные в расходе в этой группе ✅
    высчитываем долги ✅
    создаем запись о расходе и записи в expensesplit ✅

    @get("all_debts")
    получаем группу и пользователя
    проверяем есть ли доступ к группе
    вытащить все расходы из бд и посчитать
    вернуть красивое отображение, кто кому сколько должен

    @get("clever_repay")
    получаем группу и пользователя
    проверяем есть ли доступ к группе
    вытащить все расходы из бд и посчитать
    преобразовать, так чтобы каждый был должен только одному пользователю
    вернуть красивое отображение

    * по желанию
    @post("pay_debts)
    вернуть все долги, как будто все друг другу заплатили
"""


@router.post("/add_expense")
async def create_new_expense(
    group_id: int,
    expense: ExpenseCreate,
    session=Depends(get_db),
    user_id: int = Depends(get_current_user_from_token),
) -> str:
    result = await create_expense(
        group_id=group_id, expense_data=expense, session=session, user_id=user_id
    )
    return result


@router.post("/get_all/group/{group_id}", response_model=list[ExpenseDTO])
@validate_user_membership_in_group()
async def get_all_expenses_for_group(
    group_id: int,
    session=Depends(get_db),
    user_id=Depends(get_current_user_from_token),
):
    expenses = await select_all_group_expenses(group_id, session)
    return expenses
