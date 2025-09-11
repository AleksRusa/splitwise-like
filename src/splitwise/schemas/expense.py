"""
class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"

    id = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(64))
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    group_id = mapped_column(Integer, ForeignKey("groups.id", ondelete="CASCADE"))
    user_paid_id = mapped_column(Integer, ForeignKey("users.id"))

class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = mapped_column(Integer, primary_key=True)
    expense_id = mapped_column(
        Integer, ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False
    )
    user_owes_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    user_paid_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
"""

from decimal import Decimal
from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    description: str
    amount: Decimal
    group_id: int
    user_paid_id: int
