# The Travel Plan

## What the Travel Plan Is

The travel plan is the day-by-day record of the trip — where the traveler is, what they're doing, and when. It is the **single source of truth**, generated as a structured artifact after intake and maintained throughout. It exists regardless of which tools are connected; connected itinerary apps are sync targets, not the source of truth.

## Structure

Organize the plan by day. For each day include:
- Date and location
- Transport legs (departures, arrivals, transfers)
- Accommodation (check-in / check-out)
- Activities and bookings with times where known
- Any relevant notes (e.g. confirmation numbers, addresses)

## The plan artifact

Always generate a markdown file named after the destination (e.g. `tokyo-itinerary.md`) — even when a connected itinerary app is present. This is the canonical copy and the local fallback. Keep it updated as the trip evolves — add new days, update activities, and note changes. Confirm updates with the user before writing them, unless the user directed the change.

## Syncing to a connected itinerary app

If an itinerary app or notes tool is connected (Wanderlog, Notion, Google Docs, etc.), offer to export the plan there in addition to the markdown artifact, matching the app's native structure where possible. Import any changes made in the app back into the plan (and update the markdown artifact accordingly). Confirm before exporting. If multiple itinerary apps are connected, ask the user which to sync to.

## Updating

Confirm updates before writing them, unless the user directed the change. For returning users, update only what's changed since the last session — do not regenerate the full plan unless asked.
