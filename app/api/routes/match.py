from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.match import Match
from app.schemas.match import MatchSchema
from datetime import datetime
from app.services import match_service

router = APIRouter()

@router.get("/", response_model=List[MatchSchema])
def get_today_matches(db: Session = Depends(get_db)):
    """ဒီနေ့ပွဲစဉ်များကို ရယူရန် (Default)"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    return match_service.get_matches_by_date_range(db, today_str)

@router.get("/live", response_model=List[MatchSchema])
def get_live_matches(db: Session = Depends(get_db)):
    """လက်ရှိကစားနေသော ပွဲစဉ်များကို ရယူရန်"""
    results = match_service.get_live_matches_from_db(db)
    if not results:
        # Logging and minor checks can stay in routes for debugging
        pass
    return results

@router.get("/searchmatchwithoutdate/league={league_id}/season={season}", response_model=List[MatchSchema])
def search_matches_without_date(league_id: int, season: int, db: Session = Depends(get_db)):
    """ရက်စွဲမပါဘဲ League နှင့် Season အလိုက် ပွဲစဉ်များကို ရှာဖွေရန်"""
    return match_service.get_matches_by_league_and_season(db, league_id, season)

@router.get("/{date}", response_model=List[MatchSchema])
def get_matches_by_specific_date(date: str, db: Session = Depends(get_db)):
    """သတ်မှတ်ထားသော ရက်စွဲ (YYYY-MM-DD) အလိုက် ပွဲစဉ်များကို ရှာဖွေရန်"""
    try:
        return match_service.get_matches_by_date_range(db, date)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid date format. Please use YYYY-MM-DD"
        )