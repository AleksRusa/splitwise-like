from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from splitwise.database import Base
from .mixins import TimestampMixin


class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(String(256))
    group_owner_id = mapped_column(Integer, ForeignKey("users.id"))
    join_token = mapped_column(String(64), unique=True, index=True)

    owner = relationship("User", foreign_keys=[group_owner_id])
    members = relationship(
        "User",
        secondary="group_membership",
        back_populates="groups",
        cascade="all, delete",
    )
    expenses = relationship(
        "Expense",
        back_populates="group",
        cascade="all, delete-orphan",
    )
