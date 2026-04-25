from sqlalchemy.orm import Session
from app.models.match import Match
from app.models.h2h import H2H
from app.services.api_football import fetch_h2h, fetch_fixture_by_id
from app.services.match_service import save_matches
from datetime import datetime, timedelta
import asyncio

async def get_or_sync_h2h(db: Session, match_id: int):
    """
    H2H data ကို DB တွင်ရှာသည်။ မရှိလျှင် သို့မဟုတ် ဟောင်းနေလျှင် API မှ Sync လုပ်ပေးသည်။
    """
    # ၁။ Match ရှိမရှိ အရင်စစ်ဆေးသည်
    existing_match = db.query(Match).filter(Match.match_id == match_id).first()
    
    if not existing_match:
        # Match မရှိလျှင် fixture details အရင်သွားယူသည်
        match_data = await fetch_fixture_by_id(match_id)
        if match_data and match_data.get("response"):
            await asyncio.to_thread(save_matches, db, match_data)
            existing_match = db.query(Match).filter(Match.match_id == match_id).first()
        
        if not existing_match:
            return None

    # ၂။ H2H ကို DB ထဲမှာ ရှာပါ
    h2h_record = db.query(H2H).filter(H2H.match_id == match_id).first()

    # ၃။ Sync လုပ်ရန် လိုအပ်ချက်များကို စစ်ဆေးခြင်း
    is_empty = h2h_record is None or h2h_record.h2h_data is None
    
    # H2H data သည် ခဏခဏ မပြောင်းလဲနိုင်သဖြင့် ၂၄ နာရီတစ်ခါမှသာ refresh လုပ်ရန် သတ်မှတ်နိုင်သည်
    is_outdated = False
    if h2h_record and h2h_record.updated_at:
        is_outdated = (datetime.now() - h2h_record.updated_at) > timedelta(days=1)

    if is_empty or is_outdated:
        # Home Team ID နှင့် Away Team ID ကို သုံးပြီး H2H ရှာရန် parameter ပြင်ဆင်သည်
        h2h_param = f"{existing_match.home_id}-{existing_match.away_id}"
        print(f"Syncing H2H for match {match_id} (Teams: {h2h_param})...")
        
        api_data = await fetch_h2h(h2h_param)
        
        if api_data and api_data.get("response"):
            h2h_payload = api_data["response"]
            # DB Update (Blocking call ကို thread မှာ run သည်)
            h2h_record = await asyncio.to_thread(save_h2h_record, db, match_id, h2h_payload)
        else:
            print(f"No H2H data found from API for match {match_id}.")
            return h2h_record
            
    return h2h_record

def save_h2h_record(db: Session, match_id: int, h2h_data: list):
    """H2H record ကို database တွင် save သို့မဟုတ် update လုပ်ပေးသည်"""
    try:
        record = db.query(H2H).filter(H2H.match_id == match_id).first()
        if record:
            record.h2h_data = {"data": h2h_data}
            record.updated_at = datetime.now()
        else:
            record = H2H(match_id=match_id, h2h_data={"data": h2h_data})
            db.add(record)
        
        db.commit()
        db.refresh(record)
        print(f"H2H data for match {match_id} synced successfully.")
        return record
    except Exception as e:
        db.rollback()
        print(f"Database error during H2H sync for match {match_id}: {e}")
        return None