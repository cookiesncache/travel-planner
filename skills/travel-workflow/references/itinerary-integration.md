# Itinerary Integration

## What the Itinerary Is

The itinerary is the day-by-day trip plan — where the traveler is, what they're doing, and when. It is the source of truth for the travel plan — the single most capable connected itinerary tool, as determined by the capability tiers in SKILL.md Step 1.

## Structure

Organise the itinerary by day. For each day include:
- Date and location
- Transport legs (departures, arrivals, transfers)
- Accommodation (check-in / check-out)
- Activities and bookings with times where known
- Any relevant notes (e.g. confirmation numbers, addresses)

## Connected app

If an itinerary app or notes tool is connected (Wanderlog, Notion, Google Docs, etc.), create and maintain the itinerary there. Match the app's native structure where possible.

## No app connected

Generate a markdown file named after the destination (e.g. `tokyo-itinerary.md`). Keep it updated as the trip evolves — add new days, update activities, and note any changes the user confirms.

## Updating

Only add or change what the user confirms. For returning users, update only what's changed since the last session — do not regenerate the full itinerary unless asked.
