# Feasibility Integration

A pre-booking pacing review of the draft itinerary, run by the `feasibility-check` agent. The agent is **read-only** — it never writes the plan or a connector and never books. It does the per-leg estimation and flagging; this file defines the rules it applies and how the workflow invokes it.

## When the check runs

As **Step 3**, immediately after the day-by-day plan exists (Step 2) and **before** Steps 4–6 (scheduling, task sync, reminders) and before the user books — never only after bookings are confirmed. Once flights, lodging, and the rental car are locked, the cheap fixes (rebalance nights, change base towns) are gone and the trip is stuck in whatever shape it was booked in.

- **Road trip / multi-destination** (any trip with inter-stop driving) — run automatically.
- **Flight / city break** — offer it; run a lighter version (intra-day load and transfer times).
- **Returning user, already booked** (trip still upcoming) — still run, but frame findings as *manage-only* (reset expectations, minor trims) and note that pre-booking was the time to fix.
- **Trip in progress or already passed** — skip; pacing is moot once travel is underway.

## What a "leg" is

Each consecutive pair of stops on a day, plus lodging→first-stop and last-stop→lodging. Every leg gets an estimated drive time and distance.

## Drive-time source

There is no maps/routing connector. Estimate via **WebSearch/WebFetch** ("driving time A to B") and cite the source; if unavailable or inconclusive, fall back to geographic knowledge marked **low confidence**. Always attach a confidence level and source to every estimate — a guess presented as fact is worse than an honest range.

## Thresholds (defaults — tune here)

- **Heavy driving day** — total > ~5 h → flag.
- **Effectively a transit day** — total > ~7 h → the day is transit, not sightseeing.
- **Mislabeled** — a day labeled sightseeing/activity whose driving dominates usable daytime (roughly, drive time > half the daylight hours, or > ~5 h) → flag the mislabel.
- **Rushed stop** — time at a stop below a sensible minimum for its type (e.g. a national park with < half a day, a city highlight with < ~2 h).
- **Under-used stop** — far more time parked at a stop than the planned activities use.
- **Geo-inconsistent lodging** — base town well off the day's activity cluster (a long dead-leg to or from where the day is actually spent).
- **Departure-day backtrack** — on a fly-out day the route goes the wrong way past the airport, adding hours on the worst possible day.

## Flag types

`over-packed-driving` · `mislabeled-transit` · `rushed-stop` · `underused-stop` · `geo-inconsistent-lodging` · `departure-day-backtrack`

## Rebalancing options

For every flag, give at least one concrete, still-cheap option: move a night between towns, change a base town, reorder stops, split a transit day into two, or drop/shorten a stop. Frame as "while nothing is booked, you can…".

## After the check

Present the agent's report to the user, grouped by day, with confidence and sources. Let the user adjust the plan (gate 1 applies to any Claude-initiated plan edits — see `sync-protocol.md`) or accept the trade-offs, then proceed to Steps 4–6. The check informs decisions; it never books, cancels, or writes to a connector.
