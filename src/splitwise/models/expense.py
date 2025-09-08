from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    DateTime,
    func,
    DECIMAL,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .mixins import TimestampMixin
from splitwise.database import Base


class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"

    id = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(64))
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    group_id = mapped_column(Integer, ForeignKey("groups.id"))
    user_paid_id = mapped_column(Integer, ForeignKey("users.id"))

    splits = relationship("ExpenseSplit", back_populates="expense")
    payer = relationship("User", foreign_keys=[user_paid_id])


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = mapped_column(Integer, primary_key=True)
    expense_id = mapped_column(Integer, ForeignKey("expenses.id"), nullable=False)
    user_owes_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    user_paid_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)

    expense = relationship("Expense", back_populates="splits")
    user_owes = relationship("User", foreign_keys=[user_owes_id])
    user_paid = relationship("User", foreign_keys=[user_paid_id])

    __table_args__ = (UniqueConstraint("expense_id", "user_owes_id", "user_paid_id"),)
