# Itinerary Integration

## Structure

Organize the plan by day. For each day include:
- Date and location
- Transport legs (departures, arrivals, transfers)
- Accommodation (both check-in and check-out dates)
- Activities and bookings with times where known
- Any relevant notes (e.g. confirmation numbers, addresses)

## Spending Tracker

Include a **Spending Tracker** section in the plan. Whenever a booking is captured to the plan (from email, user input, or a connector), add a row. Adding the row is part of the same plan write that captured the booking — it carries the same authorization, so no separate confirmation is needed beyond what already approved capturing the booking.

**Do not add a row for a booking that was not captured as confirmed** — e.g. a payment-rejected or declined confirmation (see `email-integration.md`). Those are flagged "needs attention" and never appear in the tracker.

Format:

```markdown
## Spending Tracker

| Item | Amount | Confirmation # |
|---|---|---|
| Tokyo flight (JAL 123) | $450 | ABC123 |
| Hotel Shinjuku (3 nights) | $600 | XYZ789 |
| **Total spent** | **$1,050** | |
| **Trip budget** | **$3,000** | |
| **Remaining** | **$1,950** | |
```

- **Amount known** — record it in the row.
- **Amount unknown** (not in the confirmation, or imported from a connector that carries no price) — add the row with the Amount left blank and confirm the amount with the user. Until an amount is provided, exclude that row from the Total (do not count it as $0) and note that unpriced bookings exist, so Remaining is never silently wrong.
- Recalculate Total (sum of known amounts only) and Remaining after every change.
- The Trip budget comes from intake (Step 1). If no budget was set, omit the budget and remaining rows until one is established.

## Syncing to a connected itinerary app

If an itinerary app or notes tool is connected (Wanderlog, Notion, Google Docs, etc.), offer to export the plan there in addition to the markdown file, matching the app's native structure where possible. Import any changes made in the app back into the plan (and update the markdown file accordingly). Confirm before exporting. If multiple itinerary apps are connected, ask the user which to sync to.

## Updating

Confirm updates before writing them, unless the user directed the change. For returning users, update only what's changed — do not regenerate the full plan unless asked.

If the prior markdown file cannot be located in the current session, ask the user whether to regenerate it from context and connected tools, or start the first-time flow from scratch.
