# Email Integration

Only use this if an email app is connected. Skip silently if not — do not mention it to the user.

## What to Search For

Run targeted searches for booking confirmations:
- Flights: "flight confirmation", "flight booking", "e-ticket"
- Hotels: "hotel reservation", "hotel confirmation"
- Rental cars: "rental car reservation", "car hire confirmation"
- Tours / attractions: "booking confirmation", "ticket", "reservation"

Narrow searches by the trip date range where possible.

## What to Do With Results

- Extract only: booking type, vendor, date(s), and confirmation number where available
- Do not read or summarize full email content
- Cross-reference against all connected tools to deduplicate — if a booking already appears in any connected tool, it's captured. Only surface it as missing if it isn't reflected in the source of truth.
- Surface anything not yet captured and offer to add it to the itinerary and/or calendar as appropriate (including confirmation number) — also add a corresponding task if a task tool is connected
- Treat a confirmation email as confirmed. Flag anything that looks structurally incomplete (e.g. missing return leg, no confirmation number). If payment appears rejected or declined, attempt to identify the corresponding booking already captured in context and offer to remove it. If no clear match can be derived, ask the user before taking any action.
