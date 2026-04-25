import asyncio
from datetime import datetime
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import SessionLocal
from app.api.routes import match, standing, lineup, h2h, event
from app.services.api_football import fetch_fixtures, fetch_standings
from app.services.match_service import save_matches
from app.services.standing_service import save_standings

from contextlib import asynccontextmanager
from app.models.h2h import H2H # Ensure model is loaded for Base.metadata
from app.models.event import Event

# Logger ကို စနစ်တကျ သတ်မှတ်ခြင်း
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_match_data_task():
    """မိနစ် ၃၀ တစ်ကြိမ် data သွားယူမည့် background task"""
    while True:
        try:
            db = None # Initialize db to None
            try: # Inner try-except for database operations and API calls
                db = SessionLocal() # Assign db inside the try block
                logger.info("Background sync for matches starting...")
                today = datetime.now().strftime("%Y-%m-%d")

                # 1. Sync Matches
                data = await fetch_fixtures(today)
                if data and data.get("response"): # Check if API returned valid data
                    await asyncio.to_thread(save_matches, db, data)
                    logger.info("Match sync completed successfully.")
                else:
                    logger.warning(f"No match data fetched for {today} or API error.")
                
            except asyncio.CancelledError:
                # Task ကို cancel လုပ်ရင် ဒီကနေ တိုက်ရိုက် ပြန် raise လုပ်ပေးရမယ်
                raise
            except Exception as e:
                logger.error(f"Error during background match sync: {e}")
            finally:
                if db: # Check if db was successfully assigned before trying to close
                    db.close()

            await asyncio.sleep(1800)
        except asyncio.CancelledError:
            logger.info("Background sync task cancelled.")
            break # Task cancelled, exit the loop
        except Exception as e:
            logger.error(f"Unexpected error in background task: {e}")
            await asyncio.sleep(10) # Error တက်ရင် ၁၀ စက္ကန့်နားပြီးမှ ပြန်စမယ်

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pro Tip: Base.metadata.create_all ကို ဖယ်လိုက်ပါ၊ 
    # အခု ငါတို့က alembic ကို သုံးပြီး schema ပြောင်းလဲမှုတွေကို စနစ်တကျ လုပ်နေပြီဖြစ်လို့ပါ။
    logger.info("Application starting up...")
    
    # Server တက်လာတာနဲ့ background task ကို စတင်မည်
    sync_task = asyncio.create_task(update_match_data_task())
    yield
    # Server ပိတ်လျှင် task ကို ရပ်ခိုင်းပြီး ရပ်သွားသည်အထိ စောင့်မည်
    sync_task.cancel()
    try:
        await sync_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

# Request များကို Log ထုတ်ပေးမည့် Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    # Request path နှင့် method ကို print ထုတ်ခြင်း
    logger.info(f"Incoming {request.method} request to: {request.url.path}")
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Finished {request.method} {request.url.path} - Duration: {process_time:.4f}s")
    return response

# CORS Middleware - Flutter app မှ ခေါ်ယူနိုင်ရန်
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(match.router, prefix="/matches", tags=["matches"])
app.include_router(standing.router, prefix="/standings", tags=["standings"])
app.include_router(lineup.router, prefix="/lineups", tags=["lineups"])
app.include_router(h2h.router, prefix="/h2h", tags=["h2h"])
app.include_router(event.router, prefix="/events", tags=["events"])

@app.get("/")
def root():
    return {"message": "Football API Backend Running"}