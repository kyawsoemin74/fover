from pydantic import BaseModel
from typing import Any, Dict, List
from datetime import datetime

class EventSchema(BaseModel):
    id: int
    match_id: int
    event_data: Dict[str, Any]
    updated_at: datetime

    class Config:
        from_attributes = True