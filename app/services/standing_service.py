from app.models.standing import Standing
from sqlalchemy.orm import Session

def save_standings(db: Session, data: dict):
    responses = data.get("response", [])
    if not responses:
        params = data.get("parameters", {})
        print(f"No standings found in the API response for parameters: {params}")
        return

    for response in responses:
        league_data = response.get("league", {})
        league_id = league_data.get("id")
        country = league_data.get("country")
        standings_lists = league_data.get("standings", [])

        # Performance အတွက် ရှိပြီးသား standings တွေကို တစ်ခါတည်း ဆွဲထုတ်ထားမည်
        existing_standings = db.query(Standing).filter(Standing.league_id == league_id).all()
        existing_map = {s.team_id: s for s in existing_standings}

        for standing_list in standings_lists:
            for item in standing_list:
                team_id = item["team"]["id"]
                existing_standing = existing_map.get(team_id)

                standing_dict = {
                    "league_id": league_id,
                    "rank": item["rank"],
                    "country": country,
                    "team_id": team_id,
                    "team_name": item["team"]["name"],
                    "team_logo": item["team"]["logo"],
                    "played": item["all"]["played"],
                    "win": item["all"]["win"],
                    "draw": item["all"]["draw"],
                    "lose": item["all"]["lose"],
                    "goals_for": item["all"]["goals"]["for"],
                    "goals_against": item["all"]["goals"]["against"],
                    "points": item["points"]
                }

                if existing_standing:
                    # ရှိပြီးသားဆိုလျှင် update လုပ်သည်
                    for key, value in standing_dict.items():
                        setattr(existing_standing, key, value)
                else:
                    # မရှိသေးလျှင် အသစ်ထည့်သည်
                    new_standing = Standing(**standing_dict)
                    db.add(new_standing)

    try:
        db.commit()
        print(f"Standings for League {league_id} synced successfully.")
    except Exception as e:
        db.rollback()
        print(f"Database error during standings sync: {e}")