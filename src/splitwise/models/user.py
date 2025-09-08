from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .mixins import TimestampMixin
from splitwise.database import Base


class GroupMembers(Base):
    __tablename__ = "group_membership"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    group_id = mapped_column(Integer, ForeignKey("groups.id"))
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)

    groups = relationship(
        "Group", secondary="group_membership", back_populates="members"
    )
