from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func

from datetime import datetime, timezone

from app.database.models.base import Base


class UserTable(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[bool] = mapped_column(default=True, nullable=False)
