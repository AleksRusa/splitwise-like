"""
class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(String(256))
    group_owner = mapped_column(Integer, ForeignKey("users.id"))
    join_token = mapped_column(String(256)

    owner = relationship("User")
    members = relationship(
        "User", secondary="group_membership", foreign_keys=[group_owner]
    )

"""

from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    description: str
