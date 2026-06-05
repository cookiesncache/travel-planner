# Email Integration

Only use this if an email app is connected.

## What to Search For

Run targeted searches for booking confirmations:
- Flights: "flight confirmation", "flight booking", "e-ticket"
- Hotels: "hotel reservation", "hotel confirmation"
- Rental cars: "rental car reservation", "car hire confirmation"
- Tours / attractions: "booking confirmation", "ticket", "reservation"

Where possible, narrow searches by looking for confirmations whose content references dates within the trip date range — not by filtering emails by their received date.

## What to Do With Results

- Extract only: booking type, vendor, date(s), and confirmation number where available
- Do not read or summarize full email content
- Cross-reference against the travel plan: surface a booking if it is not yet in the plan, regardless of whether it appears in any other connected tool. If it's already in the plan, don't re-surface it.
- For anything missing, offer to add it to the plan (including confirmation number). Once confirmed, offer to export to the relevant connectors.

When a booking is captured to the plan as confirmed, add a Spending Tracker row for it — see `itinerary-integration.md` for the row format and total/remaining handling. Use the amount from the confirmation if present; if absent, follow the unknown-amount handling there. Do not add a tracker row for bookings that are not captured as confirmed (e.g. payment-rejected).

If the confirmed booking fulfills an open task (e.g. a flight confirmation fulfills "Book flights"), follow the completion-sync rule in `task-integration.md` — ask the user, then call the app's completion action.

Handle each confirmation according to its state:
- **Valid confirmation** — offer to add it to the plan (gate 1 applies for Claude-initiated additions; user-directed additions act directly). Once captured, add its Spending Tracker row.
- **Structurally incomplete** (missing return leg, no confirmation number) — flag the gap before adding; do not add silently
- **Payment rejected or declined** — confirm with the user before making any changes, then flag the corresponding booking in the plan as "needs attention" and create a task to resolve it; do not add as a confirmed booking and do not add a Spending Tracker row. If no matching booking is found in the plan, surface the rejected confirmation to the user with a summary and ask whether to add a placeholder task to investigate.
