from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from splitwise.database import Base
from .mixins import TimestampMixin


class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(String(256))

    members = relationship(
        "User", secondary="group_membership", back_populates="groups"
    )
