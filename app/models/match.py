from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, unique=True, index=True, nullable=False) # API မှ match_id ကို primary key အဖြစ်ထားသင့်

    league_id = Column(Integer)
    league_name = Column(String(255))
    league_logo = Column(String(255))
    country = Column(String(100), nullable=True) # အသစ်ထပ်ထည့်လိုက်သော country column

    home_team = Column(String(100))
    home_id = Column(Integer)
    home_logo = Column(String(255))

    away_team = Column(String(100))
    away_id = Column(Integer)
    away_logo = Column(String(255))

    status = Column(String(50))
    match_time = Column(DateTime)
    score = Column(String(20)) # Home-Away format

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) # Lineup data ကို သိမ်းဆည်းရန်
    
    lineup = relationship("Lineup", back_populates="match", uselist=False) # One-to-one relationship

    # New fields for match preview data
    referee = Column(String(255), nullable=True)
    venue_name = Column(String(255), nullable=True)
    venue_city = Column(String(255), nullable=True)
    league_round = Column(String(100), nullable=True)