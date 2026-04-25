from sqlalchemy import Column, Integer, String
from app.core.database import Base

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(255))
    xkom = Column(String(50))
    morele = Column(String(50))
    mediaexpert = Column(String(50))
    cheapest = Column(String(50))
    most_expensive = Column(String(50))
