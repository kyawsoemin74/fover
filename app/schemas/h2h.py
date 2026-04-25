from pydantic import BaseModel
from typing import Any, Dict
from datetime import datetime

class H2HSchema(BaseModel):
    id: int
    match_id: int
    h2h_data: Dict[str, Any]
    updated_at: datetime

    class Config:
        from_attributes = True