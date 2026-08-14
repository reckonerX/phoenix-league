"""
Regenerates data/managers.json from data/seasons.json (stats) and
data/current-roster.json (who's actually on the roster right now).

seasons.json is the source of truth for STATS -- never hand-edit managers.json's
career numbers directly.

current-roster.json is the source of truth for MEMBERSHIP (current vs alumni).
This is intentionally separate from stats: a brand new manager has zero games
played but is still "current" the moment they join, and an outgoing manager
should flip to "alumni" immediately, not whenever next season's data gets
entered. Update current-roster.json by hand the moment membership changes.

To add a new season's stats:
  1. Add one new object to the "seasons" array in seasons.json.
  2. Run this script: python3 compute_managers.py

To handle a manager joining/leaving:
  1. Update the "current_slugs" list in current-roster.json immediately.
  2. Run this script: python3 compute_managers.py
  (A new manager with no games yet will still appear, with all-zero stats,
  as long as they're in current-roster.json and display_names.json.)

Run from the phoenix-league/ directory, or adjust the paths below.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent
SEASONS_PATH = DATA_DIR / "seasons.json"
MANAGERS_PATH = DATA_DIR / "managers.json"
DISPLAY_NAMES_PATH = DATA_DIR / "display_names.json"
CURRENT_ROSTER_PATH = DATA_DIR / "current-roster.json"

SHRINKAGE_K = 20  # "phantom games" at league average, for weighted win%

def main():
    with open(SEASONS_PATH) as f:
        seasons = json.load(f)
    with open(DISPLAY_NAMES_PATH) as f:
        display_names = json.load(f)
    with open(CURRENT_ROSTER_PATH) as f:
        current_slugs = set(json.load(f)["current_slugs"])

    existing_photos = {}
    if MANAGERS_PATH.exists():
        with open(MANAGERS_PATH) as f:
            for m in json.load(f):
                existing_photos[m["slug"]] = m.get("photo")

    per_manager = {}
    for s in seasons:
        yr = s["year"]
        standings = s.get("standings", [])
        records = s.get("records", {})
        for slug, rec in records.items():
            m = per_manager.setdefault(slug, {
                "years_active": [], "wins": 0, "losses": 0,
                "championships": 0, "playoff_appearances": 0,
                "championship_appearances": 0, "runner_up_finishes": 0,
                "finishes": []
            })
            m["years_active"].append(yr)
            m["wins"] += rec["wins"]
            m["losses"] += rec["losses"]
            if slug in standings:
                pos = standings.index(slug) + 1
                m["finishes"].append(pos)
                if pos == 1:
                    m["championships"] += 1
                if pos <= 2:
                    m["championship_appearances"] += 1
                if pos == 2:
                    m["runner_up_finishes"] += 1
                if pos <= 6:
                    m["playoff_appearances"] += 1

    # Make sure every current-roster slug exists even with zero games played
    # (e.g. a brand new manager who hasn't played a season yet).
    for slug in current_slugs:
        per_manager.setdefault(slug, {
            "years_active": [], "wins": 0, "losses": 0,
            "championships": 0, "playoff_appearances": 0,
            "championship_appearances": 0, "runner_up_finishes": 0,
            "finishes": []
        })

    total_w = sum(m["wins"] for m in per_manager.values())
    total_g = sum(m["wins"] + m["losses"] for m in per_manager.values())
    league_avg = total_w / total_g if total_g else 0

    managers_out = []
    for slug, m in per_manager.items():
        games = m["wins"] + m["losses"]
        win_pct = round(m["wins"] / games, 4) if games else 0
        win_pct_adj = round((m["wins"] + SHRINKAGE_K * league_avg) / (games + SHRINKAGE_K), 4) if (games or league_avg) else 0
        photo = existing_photos.get(slug)
        managers_out.append({
            "slug": slug,
            "display_name": display_names.get(slug, slug),
            "status": "current" if slug in current_slugs else "alumni",
            "years_active": sorted(m["years_active"]),
            "career": {
                "wins": m["wins"], "losses": m["losses"], "games_played": games,
                "win_pct": win_pct, "win_pct_adjusted": win_pct_adj,
                "championships": m["championships"],
                "championship_appearances": m["championship_appearances"],
                "runner_up_finishes": m["runner_up_finishes"],
                "playoff_appearances": m["playoff_appearances"],
                "best_finish": min(m["finishes"]) if m["finishes"] else None,
                "worst_finish": max(m["finishes"]) if m["finishes"] else None
            },
            "photo": photo
        })

    managers_out.sort(key=lambda m: (-m["career"]["championships"], -m["career"]["win_pct_adjusted"]))

    with open(MANAGERS_PATH, "w") as f:
        json.dump(managers_out, f, indent=2)

    current = [m["display_name"] for m in managers_out if m["status"] == "current"]
    print(f"Regenerated managers.json: {len(managers_out)} managers")
    print(f"Current roster ({len(current)}): {current}")

if __name__ == "__main__":
    main()
