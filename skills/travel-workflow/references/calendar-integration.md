# Calendar Integration

The calendar is a bidirectional sync target for the travel plan (the source of truth). Export the plan's dated items as events; import existing trip events back into the plan. Confirm Claude-initiated changes with the user unless they directed the action.

## What to Export

**Trip event:**
- A single event spanning the full trip (departure to return) — use specific times if known, otherwise all-day
- Title format: destination(s) — e.g. "Tokyo & Kyoto" or "California Road Trip"

**Individual events:**
- Flights — include departure time, airline and flight number in the description, arrival airport as location
- Hotel check-ins and check-outs
- Timed-entry bookings (museums, parks, tours) with known times
- Major planned activities with confirmed times

## Guidelines

- Confirm Claude-initiated changes before writing in either direction
- If dates or times aren't known yet, skip and offer to revisit once the plan has dates set
- Use the user's local timezone for departure events; destination timezone for arrival and in-trip events where possible
