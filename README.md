# Phoenix League — Data Foundation

This is the data layer for the league site, built from `League_History.xlsx`.
Career stats are **computed from season data**, never hand-entered — this
replaces the old "Sheet3" totals tab, which had already drifted out of sync
with the season-by-season records.

## Status: brand wired in

Real brand tokens from Claude Design are now live in `css/style.css`
(Fraunces + Public Sans, oxblood/brass/ember palette on soot background).
Logo assets, favicon, and web manifest are wired into all six pages.

Two contrast bugs were caught and fixed during integration (not brand
issues — my own placeholder CSS):
- Nav wordmark was oxblood-on-near-black (1.93:1) → now cream (13.98:1)
- Champion badge was white-on-accent (3.72:1) → now dark-on-accent (4.96:1)
- A leftover light-theme "todo flag" style was nearly invisible against
  the dark theme → fixed to use brand tokens

## Files

- `data/seasons.json` — one record per year: platform, champion, full ranked
  standings, and an (empty, for now) anecdotes array.
- `data/managers.json` — one record per person: every season they played,
  computed career totals, current/alumni status (based on whether they
  appear in the most recent season, 2024).

## Known gaps — need your input before these are load-bearing

1. **2016**: flagged `legacy_missing_data: true`. No standings or W-L exist
   for this year in your sheet. Treated as a "Legacy Season" placeholder on
   the site until (if ever) recovered.
2. **`platform` field is `null` for every season.** Need actual platform per
   year (Yahoo / ESPN / Sleeper / NFL.com / etc.) — this is both a site
   detail ("Played on Yahoo") and the actual roadmap for chasing down 2016.
3. **`bio` and `photo` are empty for every manager.** These need to be
   collected from current members and alumni — this is the anecdote/photo
   backfill project, likely via a submission form rather than you writing
   it all yourself.
4. **`anecdotes` is an empty array on every season.** Same backfill problem
   — planned as crowdsourced, not written solo.
5. Manager `status` is inferred (played in 2024 = current). If someone is
   on a break but still "in" the league, this won't catch that — flag any
   exceptions.

## Schema

```json
// managers.json entry
{
  "slug": "kyle",
  "display_name": "Kyle",
  "status": "alumni",
  "years_active": [2011, 2012, ...],
  "career": { "wins": 117, "losses": 71, "games_played": 188, "win_pct": 0.6223, "top4_appearances": 9, "championships": 4 },
  "bio": "",
  "photo": null
}

// seasons.json entry
{
  "year": 2016,
  "platform": null,
  "legacy_missing_data": true,
  "champion": null,
  "standings": [],
  "anecdotes": []
}
```
