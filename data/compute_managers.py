"""
Regenerates data/managers.json from data/seasons.json.

seasons.json is the source of truth (per-season records + standings).
managers.json is fully derived -- never hand-edit it directly.

To add a new season:
  1. Add one new object to the "seasons" array in seasons.json:
     year, platform, legacy_missing_data, champion, standings (ranked
     list of manager slugs, 1st place first), records (per-manager
     wins/losses for that year), anecdotes (usually empty to start).
  2. Run this script: python3 compute_managers.py
  3. managers.json is regenerated from scratch, including career
     totals and the weighted win% for every manager, current/alumni
     status, championships, and top-4 counts.

Run from the phoenix-league/ directory, or adjust the paths below.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent
SEASONS_PATH = DATA_DIR / "seasons.json"
MANAGERS_PATH = DATA_DIR / "managers.json"
DISPLAY_NAMES_PATH = DATA_DIR / "display_names.json"

SHRINKAGE_K = 20  # "phantom games" at league average, for weighted win%

def main():
    with open(SEASONS_PATH) as f:
        seasons = json.load(f)
    with open(DISPLAY_NAMES_PATH) as f:
        display_names = json.load(f)
    # Preserve any existing photo already set by hand
    existing_photos = {}
    if MANAGERS_PATH.exists():
        with open(MANAGERS_PATH) as f:
            for m in json.load(f):
                existing_photos[m["slug"]] = m.get("photo")

    latest_year = max(s["year"] for s in seasons)

    per_manager = {}  # slug -> {years_active: [...], wins, losses, championships, top4}
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

    total_w = sum(m["wins"] for m in per_manager.values())
    total_g = sum(m["wins"] + m["losses"] for m in per_manager.values())
    league_avg = total_w / total_g if total_g else 0

    managers_out = []
    for slug, m in per_manager.items():
        games = m["wins"] + m["losses"]
        win_pct = round(m["wins"] / games, 4) if games else 0
        win_pct_adj = round((m["wins"] + SHRINKAGE_K * league_avg) / (games + SHRINKAGE_K), 4)
        photo = existing_photos.get(slug)
        managers_out.append({
            "slug": slug,
            "display_name": display_names.get(slug, slug),
            "status": "current" if latest_year in m["years_active"] else "alumni",
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

    print(f"Regenerated managers.json: {len(managers_out)} managers, "
          f"latest season {latest_year}, league avg win% {league_avg:.4f}")

if __name__ == "__main__":
    main()
