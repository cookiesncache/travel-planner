# Email Integration

Only use this if an email app is connected. Skip silently if not — do not mention it to the user.

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
- Cross-reference against the travel plan: if a booking isn't reflected in the plan, surface it as missing — even if it already exists in a connected tool. If it's already in the plan, don't re-surface it.
- For anything missing, offer to add it to the plan (including confirmation number) then export to the relevant connectors — confirm each with the user before writing.
- Treat the booking itself as real — a confirmation email is evidence the booking exists, not tentative. Still confirm with the user before adding it to the plan (gate 1 applies). Flag anything that looks structurally incomplete (e.g. missing return leg, no confirmation number). If payment appears rejected or declined, confirm with the user before making any changes, then flag the corresponding booking in the plan as "needs attention" and create a task to resolve it — do not remove the booking. If no clear match can be derived, use context to determine the appropriate action.
