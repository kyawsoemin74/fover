
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.standing import Standing
from app.schemas.standing import StandingSchema
from typing import List
from app.services.api_football import fetch_standings
from app.services.standing_service import save_standings
from datetime import datetime

router = APIRouter()

@router.get("/{league_id}", response_model=List[StandingSchema])
def get_league_standings(league_id: int, db: Session = Depends(get_db)):
    # Database ကနေ league_id အလိုက် standings တွေကို ဆွဲထုတ်မည်
    standings = db.query(Standing).filter(Standing.league_id == league_id).order_by(Standing.rank.asc()).all()
    
    if not standings:
        # Data မရှိပါက 404 Error ပြပေးမည်
        raise HTTPException(status_code=404, detail=f"No standings found for league ID {league_id}")

    return standings

@router.post("/sync/{league_id}")
async def sync_standings_for_league(
    league_id: int,
    season: int = datetime.now().year, # Default to current year, can be overridden
    db: Session = Depends(get_db)
):
    """
    API-Football မှ သတ်မှတ်ထားသော League ID အတွက် Standings များကို ဆွဲယူပြီး Database ထဲသို့ Sync လုပ်သည်။
    """
    standing_data = await fetch_standings(league_id=league_id, season=season)
    
    # API error သို့မဟုတ် data မရှိခြင်းကို စစ်ဆေးသည်
    if not standing_data or not standing_data.get("response"):
        errors = standing_data.get("errors", [])
        error_msg = f"No data available for League ID {league_id} in Season {season}."
        if errors:
            error_msg += f" API Errors: {errors}"
        return {"message": error_msg}

    # save_standings function က db session ကို thread-safe ဖြစ်အောင် asyncio.to_thread နဲ့ ခေါ်ရပါမယ်။
    await asyncio.to_thread(save_standings, db, standing_data)
    
    return {"message": f"Standings sync initiated for League ID {league_id}, Season {season}. Check logs for details."}