# Email Integration (Optional)

Only use this if an email app is connected. Skip silently if not — do not mention it to the user.

## What to Search For

Run targeted searches for booking confirmations:
- Flights: "flight confirmation", "flight booking", "e-ticket"
- Hotels: "hotel reservation", "hotel confirmation"
- Rental cars: "rental car reservation", "car hire confirmation"
- Tours / attractions: "booking confirmation", "ticket", "reservation"

Narrow searches by the trip date range where possible.

## What to Do With Results

- Extract only: booking type, vendor, date(s), and confirmation number
- Do not read or summarize full email content
- Cross-reference against both the task project and the calendar — only surface if not already reflected in either
- Surface anything not yet captured and offer to add it as a task
- Flag any confirmation that looks incomplete (e.g. missing return leg, no confirmation number, payment not confirmed)
