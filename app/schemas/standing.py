from pydantic import BaseModel, ConfigDict

class StandingSchema(BaseModel):
    team_name: str
    rank: int
    points: int
    played: int
    win: int
    draw: int
    lose: int
    team_logo: str | None = None
    goals_for: int
    goals_against: int

    model_config = ConfigDict(from_attributes=True)