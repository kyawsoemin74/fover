from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.h2h import H2HSchema
from app.services.h2h_service import get_or_sync_h2h

router = APIRouter()

@router.get("/{match_id}", response_model=H2HSchema)
async def get_match_h2h(match_id: int, db: Session = Depends(get_db)):
    """
    ပေးထားသော Match ID ၏ အသင်းနှစ်သင်းကြား ယခင်ကစားခဲ့သော ပွဲစဉ်ရလဒ် (H2H) များကို ပြန်ပေးသည်။
    """
    h2h = await get_or_sync_h2h(db, match_id)
    
    if not h2h:
        raise HTTPException(
            status_code=404, 
            detail=f"H2H data not found for match ID {match_id}."
        )
    
    return h2h