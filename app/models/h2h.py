from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class H2H(Base):
    __tablename__ = "h2h_records"

    id = Column(Integer, primary_key=True, index=True)
    # match_id ကို base လုပ်ပြီး သိမ်းဆည်းမည် (Lineup style)
    match_id = Column(Integer, ForeignKey("matches.match_id"), unique=True, index=True, nullable=False)
    h2h_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())