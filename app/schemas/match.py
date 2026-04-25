from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class MatchSchema(BaseModel):
    match_id: int
    league_id: int
    league_name: str
    league_logo: Optional[str]
    country: Optional[str]
    home_team: str
    home_logo: Optional[str]
    away_team: str
    away_logo: Optional[str]
    status: str
    match_time: datetime
    score: str
    referee: Optional[str] = None
    venue_name: Optional[str] = None
    venue_city: Optional[str] = None
    league_round: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)