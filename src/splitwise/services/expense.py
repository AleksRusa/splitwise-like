from splitwise.schemas.expense import ExpenseCreate

from splitwise.services.group import get_group_members
from sqlalchemy.ext.asyncio import AsyncSession


async def create_expense(expensese:reate, session: AsyncSession):
    group_members = await get_group_members(data.group_id, session)
    if data.user_paid_id not in group_members:
