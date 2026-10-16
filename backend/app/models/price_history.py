from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
)

from datetime import datetime

from app.core.database import Base


class PriceHistory(Base):

    __tablename__ = "price_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    query = Column(
        String(255),
        nullable=False,
    )

    xkom = Column(
        String(100),
        nullable=True,
    )

    morele = Column(
        String(100),
        nullable=True,
    )

    mediaexpert = Column(
        String(100),
        nullable=True,
    )

    cheapest = Column(
        String(50),
        nullable=True,
    )

    most_expensive = Column(
        String(50),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )