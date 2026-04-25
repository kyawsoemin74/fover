from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.lineup import LineupSchema
from app.services.lineup_service import get_or_sync_lineup

router = APIRouter()

@router.get("/{match_id}", response_model=LineupSchema)
async def get_match_lineups(match_id: int, db: Session = Depends(get_db)):
    """
    ပွဲစဉ်တစ်ခု၏ Lineup Data များကို ပြန်လည်ရယူသည်။
    Lineup Data မရှိသေးပါက သို့မဟုတ် နောက်ဆုံး Update လုပ်ထားသည်မှာ ကြာမြင့်နေပါက
    API-Football မှ အသစ်ပြန်လည် ဆွဲယူပြီး Database တွင် သိမ်းဆည်းသည်။
    """
    lineup = await get_or_sync_lineup(db, match_id)
    
    if not lineup:
        raise HTTPException(status_code=404, detail=f"Lineup data not found for match ID {match_id}. It might not be available yet or the match ID is incorrect.")
    
    return lineup