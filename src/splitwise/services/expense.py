from collections import defaultdict
from decimal import Decimal
from fastapi import HTTPException
from splitwise.logger import logger
from splitwise.models.expense import Expense, ExpenseSplit
from splitwise.models.group import Group
from splitwise.schemas.expense import DebtItem, ExpenseCreate, ExpenseDTO

from splitwise.services.group import get_group_by_group_id, get_group_members
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
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


async def select_all_group_expenses(group_id: int, session: AsyncSession):
    try:
        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(selectinload(Group.expenses))  # ← Явно загружаем expenses
        )
        result = await session.execute(stmt)
        group = result.scalar_one_or_none()
        if not group:
            logger.error(f"group with id - '{group_id} is not found")
            raise HTTPException(status_code=403, detail=f"group not found")
        if not group.expenses:
            logger.warning(f"group_id={group_id} don't have expenses")
        else:
            logger.info(f"selected expenses for group_id={group_id}")
        return group.expenses
    except Exception as e:
        logger.error(
            f"exception - {e} while selected all expenses for group_id={group_id}"
        )
        raise e


async def get_summarize_user_expenses_in_group(
    group_id: int,
    session: AsyncSession,
    user_id: int,
):
    try:
        stmt = (
            select(ExpenseSplit)
            .join(ExpenseSplit.expense)
            .where(Expense.group_id == group_id)
            .where(
                or_(
                    ExpenseSplit.user_paid_id == user_id,
                    ExpenseSplit.user_owes_id == user_id,
                )
            )
            .order_by(ExpenseSplit.amount.asc())
        )
        result = await session.execute(stmt)
        user_splits = result.scalars().all()
        debt_map = defaultdict(Decimal)
        for split in user_splits:
            key = (split.user_owes_id, split.user_paid_id)
            debt_map[key] += split.amount
        print(debt_map)
        processed_pairs = set()
        final_debt_map = {}
        for (user_a, user_b), amount_ab in debt_map.items():
            if (user_a, user_b) in processed_pairs or (
                user_b,
                user_a,
            ) in processed_pairs:
                continue
            amount_ba = debt_map.get((user_b, user_a), Decimal("0.00"))

            if amount_ab > amount_ba:
                final_debt_map[(user_a, user_b)] = amount_ab - amount_ba
            elif amount_ba > amount_ab:
                final_debt_map[(user_b, user_a)] = amount_ba - amount_ab

            # Помечаем обе пары как обработанные
            processed_pairs.add((user_a, user_b))
            processed_pairs.add((user_b, user_a))
        debt_items = []
        for key, amount in final_debt_map.items():
            if key[0] == user_id:
                debt_items.append(
                    DebtItem(
                        direction="you_owe",
                        user_id=key[1],
                        amount=amount,
                        currency="RUB",
                    )
                )
            else:
                debt_items.append(
                    DebtItem(
                        direction="owes_you",
                        user_id=key[0],
                        amount=amount,
                        currency="RUB",
                    )
                )
        logger.info(f"selected all debts for user='{user_id}' in group='{group_id}'")
        return debt_items
    except Exception as e:
        logger.error(f"exception - {e} in selecting summarize debts")
        raise HTTPException(status_code=400, detail="failed to select debts")
