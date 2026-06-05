# Calendar Integration

The calendar is a bidirectional sync target for the travel plan (the source of truth). Export the plan's dated items as events; import existing trip events back into the plan. Confirm Claude-initiated plan updates (gate 1) and exports to the calendar (gate 2) with the user unless they directed the action. If multiple calendar tools are connected, ask the user which to use before proceeding.

## What to Export

Create calendar events **only** for the following:

- **Trip block** — a single event spanning the full trip (departure to return); specific times if known, otherwise all-day. Title: destination(s) — e.g. "Tokyo & Kyoto" or "California Road Trip".
- **Flights** — one event per leg, spanning that leg's departure to arrival; origin airport as location, destination airport plus airline and flight number in the description. A multi-leg or connecting itinerary gets a separate event for each leg.
- **Accommodation stays** — a single event per stay spanning check-in to check-out, using the check-in and check-out times where known (otherwise the respective dates).
- **Timed-entry attractions** — timed events for anything with a confirmed entry or start time (museums, parks, tours, reservations); include the entry time.

**Do not create calendar events** for pre-trip action tasks, prep reminders, or planning tasks (e.g. "book flights", "apply for visa", "pack", "confirm reservations 48h out"). These are handled through task and reminder capability logic only — see `task-integration.md` and `reminder-integration.md`. A timed-entry attraction may still have an associated prep task (e.g. "bring confirmation"); that task goes to the task app, not the calendar.

## Guidelines

- Confirm Claude-initiated plan updates (gate 1) before importing; confirm exports to the calendar (gate 2) before creating events
- When importing, skip any event already reflected in the plan — do not surface it again
- If dates or times aren't known yet, skip and offer to revisit once the plan has dates set
- Use the departure city timezone for departure events and the destination timezone for arrival and in-trip events. For multi-destination trips, apply this per leg — each segment uses its own origin and destination timezones. If a timezone can't be inferred, ask the user; if still unknown, use UTC and note it in the event
