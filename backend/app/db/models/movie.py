from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    poster_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    release_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    runtime_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vote_average: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    movie_genres: Mapped[List["MovieGenre"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    room_movies: Mapped[List["RoomMovie"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    swipes: Mapped[List["Swipe"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    matches: Mapped[List["Match"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
