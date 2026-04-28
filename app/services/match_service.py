import logging
from app.models.match import Match
from datetime import datetime, time
from typing import List
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def map_match_data(item: dict) -> dict:
    """API response item ကို database field mapping ပြောင်းပေးသော helper function"""
    fixture = item.get("fixture", {})
    league = item.get("league", {})
    
    mapped_data = {
        "league_id": league.get("id"),
        "league_name": league.get("name"),
        "league_logo": league.get("logo"),
        "country": league.get("country"),
        "home_team": item.get("teams", {}).get("home", {}).get("name"),
        "home_id": item.get("teams", {}).get("home", {}).get("id"),
        "home_logo": item.get("teams", {}).get("home", {}).get("logo"),
        "away_team": item.get("teams", {}).get("away", {}).get("name"),
        "away_id": item.get("teams", {}).get("away", {}).get("id"),
        "away_logo": item.get("teams", {}).get("away", {}).get("logo"),
        "status": fixture.get("status", {}).get("short"),
        "match_time": datetime.fromisoformat(fixture.get("date").replace('Z', '+00:00')) if fixture.get("date") else datetime.now(),
        "score": f"{item['goals']['home'] or 0}-{item['goals']['away'] or 0}",
        "referee": fixture.get("referee"),
        "venue_name": fixture.get("venue", {}).get("name"),
        "venue_city": fixture.get("venue", {}).get("city"),
        "league_round": league.get("round"),
    }
    return mapped_data

def save_matches(db, data):
    fixtures = data.get("response", [])
    if not fixtures:
        logger.warning("No fixtures found in the API response.")
        return
    
    incoming_match_ids = [item["fixture"]["id"] for item in fixtures]
    logger.info(f"Syncing {len(incoming_match_ids)} matches with database...")

    # Database ထဲမှာ ရှိနှင့်ပြီးသား Match တွေကို တစ်ခါတည်း ဆွဲထုတ်ခြင်း (N+1 Query problem ကို ရှောင်ရန်)
    existing_matches = db.query(Match).filter(Match.match_id.in_(incoming_match_ids)).all()
    existing_matches_map = {m.match_id: m for m in existing_matches}

    new_matches_to_add = []
    updated_count = 0
    
    for item in fixtures:
        match_id = item["fixture"]["id"]
        match_data = map_match_data(item)
        existing_match = existing_matches_map.get(match_id)

        if existing_match:
            # Update existing record attributes only if they have changed
            changed = False
            for key, value in match_data.items():
                if getattr(existing_match, key) != value:
                    setattr(existing_match, key, value)
                    changed = True
            if changed:
                updated_count += 1
        else:
            # Create new record object
            new_matches_to_add.append(Match(match_id=match_id, **match_data))
    
    if new_matches_to_add:
        db.add_all(new_matches_to_add)
        
    try:
        db.commit()
        logger.info(f"Successfully synced: Added {len(new_matches_to_add)}, Updated {updated_count}")
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during commit: {e}")

def get_matches_by_date_range(db: Session, date_str: str) -> List[Match]:
    """ရက်စွဲအလိုက် ပွဲစဉ်များကို ရှာဖွေပေးသော Service (DRY point)"""
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    start_of_day = datetime.combine(target_date, time.min)
    end_of_day = datetime.combine(target_date, time.max)
    
    return db.query(Match).filter(
        Match.match_time >= start_of_day, 
        Match.match_time <= end_of_day
    ).all()

def get_live_matches_from_db(db: Session) -> List[Match]:
    """လက်ရှိ Live ဖြစ်နေသော ပွဲစဉ်များကို ရှာဖွေပေးသော Service"""
    live_statuses = ["1H", "HT", "2H", "ET", "P", "BT", "LIVE", "INT"]
    return db.query(Match).filter(Match.status.in_(live_statuses)).all()

def get_matches_by_league_and_season(db: Session, league_id: int, season: int) -> List[Match]:
    """League ID နှင့် Season အလိုက် ပွဲစဉ်များကို ရှာဖွေပေးသော Service"""
    year_start = datetime(season, 1, 1, 0, 0, 0)
    year_end = datetime(season, 12, 31, 23, 59, 59)
    
    return db.query(Match).filter(
        Match.league_id == league_id,
        Match.match_time >= year_start,
        Match.match_time <= year_end
    ).all()