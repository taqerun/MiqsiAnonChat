from typing import List, Optional

from sqlalchemy import DateTime, func, BigInteger, String, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.mutable import MutableList, MutableDict
from sqlalchemy.orm import Mapped, mapped_column, as_declarative, relationship


@as_declarative()
class Base:
    __abstract__ = True

    created: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now()
    )
    updated: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )  # Telegram user ID

    locale: Mapped[str] = mapped_column(
        String(10), nullable=False, default="en"
    )  # User language

    gender: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True
    )

    is_premium: Mapped[bool] = mapped_column(
        Boolean, nullable=True, default=False
    )

    dialog_partner_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True
    )

    interests: Mapped[Optional[List[str]]] = mapped_column(
        MutableList.as_mutable(ARRAY(String)),
        nullable=True
    )

    friends: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB), nullable=False, default=dict
    )

    mode: Mapped[str] = mapped_column(
        String(20), nullable=False, default="default"
    )

    queue_entry: Mapped[Optional["QueueUser"]] = relationship(
        "QueueUser", back_populates="user", uselist=False
    )


class QueueUser(Base):
    """
    Represents a user currently in the queue.
    """
    __tablename__ = "queue_users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    locale: Mapped[str] = mapped_column(
        String(10), nullable=False
    )

    interests: Mapped[Optional[List[str]]] = mapped_column(
        MutableList.as_mutable(ARRAY(String)),
        nullable=True
    )

    mode: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="queue_entry"
    )


class Dialog(Base):
    __tablename__ = 'dialogs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    users: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB), nullable=False, default=dict
    )

    mode: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    is_friends: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    settings: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB), nullable=False, default=dict
    )
