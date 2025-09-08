from datetime import datetime

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .mixins import TimestampMixin
from splitwise.database import Base


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    groups = relationship(
        "Group", secondary="group_membership", back_populates="members"
    )
