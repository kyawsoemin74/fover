from sqlalchemy.orm import Session
from app.models.match import Match
from app.models.event import Event
from app.services.api_football import fetch_events, fetch_fixture_by_id
from app.services.match_service import save_matches
from datetime import datetime, timedelta
import asyncio

async def get_or_sync_events(db: Session, match_id: int):
    """Match Events (Facts) ကို DB မှရှာပြီး လိုအပ်ပါက API နှင့် Sync လုပ်သည်"""
    existing_match = db.query(Match).filter(Match.match_id == match_id).first()
    
    if not existing_match:
        match_data = await fetch_fixture_by_id(match_id)
        if match_data and match_data.get("response"):
            await asyncio.to_thread(save_matches, db, match_data)
            existing_match = db.query(Match).filter(Match.match_id == match_id).first()
        if not existing_match: return None

    event_record = db.query(Event).filter(Event.match_id == match_id).first()

    # Sync logic: Live ဖြစ်နေရင် ၂ မိနစ်တစ်ခါ refresh လုပ်မယ်
    is_finished = existing_match.status in ["FT", "AET", "PEN"]
    is_empty = event_record is None or event_record.event_data is None
    
    is_outdated = False
    if event_record and event_record.updated_at:
        refresh_interval = timedelta(minutes=60) if is_finished else timedelta(minutes=2)
        is_outdated = (datetime.now() - event_record.updated_at) > refresh_interval

    if is_empty or (is_outdated and not is_finished):
        print(f"Syncing events for match {match_id}...")
        api_data = await fetch_events(match_id)
        
        if api_data and api_data.get("response"):
            event_payload = api_data["response"]
            event_record = await asyncio.to_thread(save_event_record, db, match_id, event_payload)
            
    return event_record

def save_event_record(db: Session, match_id: int, events: list):
    try:
        record = db.query(Event).filter(Event.match_id == match_id).first()
        if record:
            record.event_data = {"data": events}
            record.updated_at = datetime.now()
        else:
            record = Event(match_id=match_id, event_data={"data": events})
            db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()
        print(f"Error saving events: {e}")
        return None