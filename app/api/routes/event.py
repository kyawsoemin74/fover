from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.event import EventSchema
from app.services.event_service import get_or_sync_events

router = APIRouter()

@router.get("/{match_id}", response_model=EventSchema)
async def get_match_events(match_id: int, db: Session = Depends(get_db)):
    """ပွဲစဉ်တစ်ခု၏ ဖြစ်ရပ်များ (Events/Facts) ကို ရယူရန်"""
    events = await get_or_sync_events(db, match_id)
    if not events:
        raise HTTPException(status_code=404, detail="Events not found")
    return events