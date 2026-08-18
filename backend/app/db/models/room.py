from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    genre: Mapped[str] = mapped_column(String(50), nullable=False)
    host_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    host: Mapped["User"] = relationship(back_populates="hosted_rooms")
    members: Mapped[List["RoomMember"]] = relationship(back_populates="room", cascade="all, delete-orphan")
    room_movies: Mapped[List["RoomMovie"]] = relationship(back_populates="room", cascade="all, delete-orphan")
    swipes: Mapped[List["Swipe"]] = relationship(back_populates="room", cascade="all, delete-orphan")
    matches: Mapped[List["Match"]] = relationship(back_populates="room", cascade="all, delete-orphan")
