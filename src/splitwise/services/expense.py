from fastapi import HTTPException
from splitwise.logger import logger
from splitwise.models.expense import Expense, ExpenseSplit
from splitwise.schemas.expense import ExpenseCreate

from splitwise.services.group import get_group_members
from sqlalchemy.ext.asyncio import AsyncSession


async def create_expense(
    group_id: int,
    expense_data: ExpenseCreate,
    session: AsyncSession,
    user_id: int,
) -> str:
    bad_request_exception = HTTPException(
        status_code=400,
        detail="can't split expense between users that are not in group",
    )
    group_members = await get_group_members(group_id, session)
    group_members = set(group_members)
    if expense_data.user_paid_id not in group_members:
        logger.error("can't split the expense between user that is not in group")
        raise bad_request_exception

    for user in expense_data.splits_between:
        if user not in group_members:
            logger.error("can't split the expense between user that is not in group")
            raise bad_request_exception
    try:
        expense = Expense(
            description=expense_data.description,
            amount=expense_data.amount,
            group_id=group_id,
            user_paid_id=expense_data.user_paid_id,
        )
        session.add(expense)
        await session.commit()
        logger.info(f"created new expense - id={expense.id}")

        result = await create_expense_splits(expense.id, expense_data, session)
        return result

    except Exception as e:
        logger.error(f"exception - {e} while creationg expense")
        raise HTTPException(status_code=400, detail="can't create expense")


async def create_expense_splits(
    expense_id: int, expense_data: ExpenseCreate, session: AsyncSession
) -> str:
    user_owes_amount = expense_data.amount / (len(expense_data.splits_between) + 1)
    for user_owes_id in expense_data.splits_between:
        try:
            expense_split = ExpenseSplit(
                expense_id=expense_id,
                user_owes_id=user_owes_id,
                user_paid_id=expense_data.user_paid_id,
                amount=user_owes_amount,
            )
            session.add(expense_split)
            await session.commit()
        except Exception as e:
            logger.error(f"exception - {e} while creationg expense splits")
            raise HTTPException(status_code=400, detail="can't create expense split")
    logger.info(f"created all splits for expense_id={expense_id}")
    return "expense added successfully"
