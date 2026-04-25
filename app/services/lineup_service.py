from sqlalchemy.orm import Session
from app.models.match import Match
from app.models.lineup import Lineup
from app.services.api_football import fetch_lineups, fetch_fixture_by_id
from app.services.match_service import save_matches
from datetime import datetime, timedelta
import asyncio

async def get_or_sync_lineup(db: Session, match_id: int):
    """
    ပွဲစဉ်တစ်ခု၏ Lineup ကို DB တွင်ရှာသည်။ မရှိလျှင် သို့မဟုတ် ဟောင်းနေလျှင် API မှ ဆွဲယူပြီး Update လုပ်ပေးသည်။
    """
    # Match ရှိမရှိ အရင်စစ်ဆေးပါ
    existing_match = db.query(Match).filter(Match.match_id == match_id).first()
    
    if not existing_match:
        # Match မရှိလျှင် API မှ အရင်သွားယူမည် (On-demand Match Sync)
        print(f"Match ID {match_id} not found. Fetching fixture details first...")
        match_data = await fetch_fixture_by_id(match_id)
        if match_data and match_data.get("response"):
            await asyncio.to_thread(save_matches, db, match_data)
            existing_match = db.query(Match).filter(Match.match_id == match_id).first()
        
        if not existing_match:
            return None

    # Lineup ကို DB ထဲမှာ ရှာပါ
    lineup = db.query(Lineup).filter(Lineup.match_id == match_id).first()

    # Lineup ပြန်ခေါ်ရန် လိုအပ်ချက်များကို စစ်ဆေးခြင်း
    is_empty = lineup is None or lineup.lineup_data is None
    # ပွဲမပြီးသေးခင် ၁ နာရီတစ်ခါ refresh လုပ်နိုင်ရန် (ဥပမာ- lineup အပြောင်းအလဲရှိလျှင်)
    # ပွဲပြီးသွားရင်တော့ lineup က ထပ်မပြောင်းတော့သဖြင့် sync လုပ်ရန်မလိုပါ
    is_outdated = False
    if lineup and lineup.updated_at:
        is_outdated = (datetime.now() - lineup.updated_at) > timedelta(hours=1)

    is_finished = existing_match.status in ["FT", "AET", "PEN", "CANC", "PST", "INT", "ABD", "WO"]

    if is_empty or (is_outdated and not is_finished):
        print(f"Syncing lineup for match {match_id}...")
        api_data = await fetch_lineups(match_id)
        
        if api_data and api_data.get("response"):
            # API ကနေ ရလာတဲ့ lineup data ကို database မှာ သိမ်းဆည်းသည်
            # API-Football ရဲ့ lineup response က list of dicts ဖြစ်တတ်ပါတယ်။
            # ဥပမာ: [{"team": {}, "startXI": [], "substitutes": []}, {"team": {}, ...}]
            lineup_payload = api_data["response"] 
            
            # DB Update (Blocking call ကို thread မှာ run သည်)
            lineup = await asyncio.to_thread(save_lineup_data, db, match_id, lineup_payload)
        else:
            print(f"No lineup data found from API for match {match_id}.")
            # API ကနေ data မရရင် ရှိပြီးသား lineup ကိုပဲ ပြန်ပေးပါ (ရှိခဲ့လျှင်)
            return lineup
            
    return lineup

def save_lineup_data(db: Session, match_id: int, lineup_data: list):
    try:
        lineup = db.query(Lineup).filter(Lineup.match_id == match_id).first()
        if lineup:
            lineup.lineup_data = {"data": lineup_data}
            lineup.updated_at = datetime.now()
        else:
            lineup = Lineup(match_id=match_id, lineup_data={"data": lineup_data})
            db.add(lineup)
        db.commit()
        db.refresh(lineup)
        print(f"Lineup data for match {match_id} synced successfully.")
        return lineup
    except Exception as e:
        db.rollback()
        print(f"Database error during lineup sync for match {match_id}: {e}")
        return None