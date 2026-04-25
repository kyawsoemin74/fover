from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Standing(Base):
    __tablename__ = "standings"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer)
    rank = Column(Integer)
    country = Column(String(100), nullable=True) # Standing တွင်လည်း country ထည့်သွင်းခြင်း

    team_id = Column(Integer)
    team_name = Column(String(100))
    team_logo = Column(String(255))

    played = Column(Integer)
    win = Column(Integer)
    draw = Column(Integer)
    lose = Column(Integer)

    goals_for = Column(Integer)
    goals_against = Column(Integer)
    points = Column(Integer)

    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())