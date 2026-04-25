import httpx
from app.core.config import settings

BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-apisports-key": settings.API_KEY
}

async def fetch_fixtures(date: str):
    url = f"{BASE_URL}/fixtures?date={date}"
    
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        return res.json()

async def fetch_h2h(h2h_param: str):
    """API-Football မှ အသင်းနှစ်သင်း၏ Head-to-Head (H2H) ရလဒ်များကို ဆွဲယူသည်"""
    url = f"{BASE_URL}/fixtures/headtohead?h2h={h2h_param}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        return res.json()

async def fetch_fixture_by_id(fixture_id: int):
    """API-Football မှ ID တစ်ခုတည်းဖြင့် ပွဲစဉ်အချက်အလက်ကို ဆွဲယူသည်"""
    url = f"{BASE_URL}/fixtures?id={fixture_id}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        return res.json()

async def fetch_standings(league_id: int, season: int):
    url = f"{BASE_URL}/standings?league={league_id}&season={season}"
    
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        return res.json()

async def fetch_lineups(fixture_id: int):
    """API-Football မှ ပွဲစဉ်တစ်ခု၏ Lineup Data များကို ဆွဲယူသည်"""
    url = f"{BASE_URL}/fixtures/lineups?fixture={fixture_id}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        return res.json()

async def fetch_events(fixture_id: int):
    """API-Football မှ ပွဲစဉ်တစ်ခု၏ ဖြစ်ရပ်များ (Events - Goals, Cards, Subs) ကို ဆွဲယူသည်"""
    url = f"{BASE_URL}/fixtures/events?fixture={fixture_id}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        return res.json()