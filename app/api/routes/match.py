from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.match import Match
from app.schemas.match import MatchSchema
from datetime import datetime
from sqlalchemy import func
from app.services.lineup_service import get_or_sync_lineup

router = APIRouter()

@router.get("/today", response_model=List[MatchSchema])
def get_matches(db: Session = Depends(get_db)):
    # ရှာဖွေမည့် ရက်စွဲကို Print ထုတ်ကြည့်ပါ
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    print(f"Filtering between: {today_start} and {today_end}")
    
    # Debug: Database ထဲမှာ စုစုပေါင်း match ဘယ်နှခုရှိနေလဲ အရင်စစ်ပါ
    total_count = db.query(Match).count()
    print(f"Total matches in DB: {total_count}")

    return db.query(Match).filter(Match.match_time >= today_start, Match.match_time <= today_end).all()

@router.get("/live", response_model=List[MatchSchema])
def get_live_matches(db: Session = Depends(get_db)):
    # Status code များ အမှားအယွင်းမရှိစေရန် 'LIVE', 'IN PLAY' စသည်တို့ကိုပါ ထည့်သွင်းစစ်ဆေးနိုင်သည်
    # သို့သော် API-Sports short status အစစ်အမှန်များမှာ အောက်ပါအတိုင်းဖြစ်သည်
    live_statuses = ["1H", "HT", "2H", "ET", "P", "BT", "LIVE", "INT"]
    results = db.query(Match).filter(Match.status.in_(live_statuses)).all()
    
    # ဘာကြောင့် 0 ဖြစ်နေလဲ သိနိုင်ရန် လက်ရှိ DB ထဲမှာ ရှိနေတဲ့ Status တွေကိုပါ Print ထုတ်ကြည့်ပါ
    if not results:
        available_statuses = db.query(Match.status).distinct().all()
        print(f"No live matches. Available statuses in DB: {available_statuses}")
    
    return results