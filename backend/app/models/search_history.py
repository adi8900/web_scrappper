from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.core.database import Base


class SearchHistory(Base):
    """Separate versioned table keeps legacy history intact."""
    __tablename__ = "search_history_v2"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    query = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
                        nullable=False)
