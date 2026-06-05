# Calendar Integration

The calendar is a bidirectional sync target for the travel plan (the source of truth). Export the plan's dated items as events; import existing trip events back into the plan. Confirm Claude-initiated plan updates (gate 1) and exports to the calendar (gate 2) with the user unless they directed the action. If multiple calendar tools are connected, ask the user which to use before proceeding.

## What to Export

**Trip event:**
- A single event spanning the full trip (departure to return) — use specific times if known, otherwise all-day
- Title format: destination(s) — e.g. "Tokyo & Kyoto" or "California Road Trip"

**Flights and timed-entry bookings** — export as calendar events (hard scheduled times):
- Flights: include departure time, airline and flight number in the description, arrival airport as location
- Timed-entry bookings (museums, parks, tours): include the entry time; also add a prep task to the plan now (e.g. "Bring timed-entry confirmation") — Step 4 will sync it to a connected task app

**Hotel check-ins** — not a timed event; export as an all-day marker on the check-in date. The associated prep actions (confirm reservation, arrange transport, collect keys) belong as tasks in Step 4, not as calendar events.

**Hotel check-outs** — add to the plan as a task with a hard deadline (e.g. "Check out by 11am"), not a calendar event.

**Major planned activities with confirmed times** — export as calendar events.

## Guidelines

- Confirm Claude-initiated plan updates (gate 1) before importing; confirm exports to the calendar (gate 2) before creating events
- When importing, skip any event already reflected in the plan — do not surface it again
- If dates or times aren't known yet, skip and offer to revisit once the plan has dates set
- Use the departure city timezone for departure events and the destination timezone for arrival and in-trip events. For multi-destination trips, apply this per leg — each segment uses its own origin and destination timezones. If a timezone can't be inferred, ask the user; if still unknown, use UTC and note it in the event
