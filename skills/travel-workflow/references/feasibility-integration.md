# Feasibility Integration

A pre-booking pacing review of the draft itinerary, run by the `feasibility-check` agent. The agent is **read-only** — it never writes the plan or a connector and never books. It does the per-leg estimation and flagging; this file defines the rules it applies and how the workflow invokes it.

## When the check runs

As **Step 3**, immediately after the day-by-day plan exists (Step 2) and **before** Steps 4–6 (scheduling, task sync, reminders) and before the user books — never only after bookings are confirmed. Once transport and lodging are booked, the cheap fixes (rebalance nights, change base towns, swap a leg's mode) are gone and the trip is stuck in whatever shape it was booked in.

- **Any trip with inter-stop travel** — a road trip, or a multi-destination trip by car, flight, train, or ferry — run automatically.
- **Single-base city break** (no inter-stop travel) — offer it; run a lighter version (intra-day load and local transfer/airport times).
- **Returning user, already booked** (trip still upcoming) — still run, but frame findings as *manage-only* (reset expectations, minor trims) and note that pre-booking was the time to fix.
- **Trip in progress or already passed** — skip; pacing is moot once travel is underway.

## What a "leg" is

Each consecutive pair of stops on a day, plus lodging→first-stop and last-stop→lodging. Every leg has a **travel mode** (drive, flight, train, ferry, transit, walk) and an estimated **door-to-door travel time** — and a distance, for driving.

## Travel-time source

There is no maps/routing connector. Estimate via **WebSearch/WebFetch** for the leg's mode ("driving time A to B", "train time A to B", "flight time A to B", "ferry schedule A to B") and cite the source; if unavailable or inconclusive, fall back to geographic/transport knowledge marked **low confidence**. Always attach a confidence level and source — a guess presented as fact is worse than an honest range.

**Count door-to-door, not in-vehicle.** For flights especially, the day's cost is air time **plus** ~3 h of airport and transfer overhead (getting to the airport, check-in/security, boarding, deplaning/bags, reaching the next city) — a short flight can still consume most of a day. Trains carry light overhead; ferries are schedule-bound.

## Meals (first-class time costs)

Meals consume real time a travel-only model misses — count both parts:

- **Detour** — the *extra* travel to reach an eatery off the through-route and rejoin it, measured against the day's route, not absolute distance. On-route ≈ 0; ~20 min off-route ≈ ~40 min round trip. Estimate via WebSearch where material; attach confidence + source.
- **Dining duration (defaults by venue type — tune here):**
  - Popular / in-demand sit-down (waits common) — ~75–90 min
  - Standard sit-down — ~60 min
  - Casual counter / quick-service — ~30–45 min
  - Tasting / multi-course — ~120 min
- A "lunch" on a long transfer day is often a mid-afternoon *arrival* meal — place it in the timeline, since it shifts everything after it.

Meal detours and dining blocks count toward the day's total like any other time cost.

## Hard deadlines

Some days have a hard time wall — a lodging **check-in / front-desk cutoff**, a **timed reservation**, a tour start. When the plan notes one, build the **meal-inclusive timeline** for the day (legs + activities + meal detours + dining, placed in clock time) and test whether it's met. Flag any deadline the day would miss or only barely make. This is exactly where meals bite: a day that's fine on driving alone can blow a 9:30 PM check-in once a 75–90 min dinner and its detour are counted. Pre-booking, flag it so the plan can change; if the item is already booked, operate manage-only — re-flag and advise, never rebook.

## Thresholds (defaults — tune here)

- **Heavy travel day** — total door-to-door travel > ~5 h → flag.
- **Effectively a transit day** — total door-to-door travel > ~7 h → the day is transit, not sightseeing. (A single flight often lands here once airport overhead and transfers are counted, even when air time is short.)
- **Over-packed day** — the day's *full* budget (travel + activities + meal detours + dining) exceeds usable daytime, even if travel alone was under the heavy-day threshold → flag. This is the meal-aware check a travel-only model misses.
- **Mislabeled** — a day labeled sightseeing/activity whose travel dominates usable daytime (roughly, travel > half the daylight hours, or > ~5 h) → flag the mislabel.
- **Rushed stop** — time at a stop below a sensible minimum for its type (e.g. a national park with < half a day, a city highlight with < ~2 h).
- **Under-used stop** — far more time parked at a stop than the planned activities use.
- **Geo-inconsistent lodging** — base town well off the day's activity cluster (a long dead-leg to or from where the day is actually spent).
- **Departure-day backtrack** — on a fly-out (or transfer-out) day the route goes the wrong way past the airport/station, adding hours on the worst possible day.

## Flag types

`over-packed-travel` · `over-packed-day` · `mislabeled-transit` · `rushed-stop` · `underused-stop` · `geo-inconsistent-lodging` · `departure-day-backtrack` · `deadline-risk`

## Rebalancing options

For every flag, give at least one concrete, still-cheap option: move a night between towns, change a base town, reorder stops, split a transit day into two, swap a leg's mode (e.g. fly instead of a long drive), swap a sit-down meal for a quicker stop, move a reservation earlier, pick lodging with late/self check-in, or drop/shorten a stop. Frame as "while nothing is booked, you can…".

## After the check

Present the agent's report to the user, grouped by day, with confidence and sources. Let the user adjust the plan (gate 1 applies to any Claude-initiated plan edits — see `sync-protocol.md`) or accept the trade-offs, then proceed to Steps 4–6. The check informs decisions; it never books, cancels, or writes to a connector.
