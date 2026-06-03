# Integrations Reference

Connected tools are bidirectional sync targets for the travel plan — never the source of truth. The plan is the source of truth (see `references/itinerary-integration.md`). Export plan data to connectors and import their data back into the plan, confirming Claude-initiated changes with the user.

## Identifying Connected Tools

Check which tools are available by looking at what tools Claude has access to in the current session. Group them by capability:

- **Calendar** — any tool that can create and read calendar events (e.g. Google Calendar, Outlook, Apple Calendar)
- **Itinerary** — any tool that can create and maintain a structured trip plan (e.g. Wanderlog, Notion, Google Docs)
- **Task management** — any tool that can create, read, and update tasks or projects (e.g. Todoist, Asana, Things, Apple Reminders)
- **Email** — any tool that can search and read emails (e.g. Gmail, Outlook)

If multiple tools of the same capability type are connected, ask the user which one to sync to for this trip.

## Session Capabilities

In addition to connected tools, check for session-level capabilities that may be available regardless of connectors:

- **Scheduled-task** — the ability to schedule a timed reminder within the session (not a connected app). Check whether scheduled-task tools are available before attempting to use them. This capability is not always present and should be treated as a last-resort fallback for reminders when no calendar or task app is connected.

## Calendar

Export the plan's dated items as calendar events; import existing trip events back into the plan.

**Trip event:**
- A single event spanning the full trip (departure to return) — use specific times if known, otherwise all-day
- Title: destination(s) — e.g. "Tokyo & Kyoto" or "California Road Trip"

**Individual events:**
- Flights (departure time, airline/flight number in description, arrival airport in location)
- Hotel check-ins and check-outs
- Timed-entry bookings (museums, parks, tours)
- Major planned activities with known times

Confirm Claude-initiated changes with the user (see SKILL.md for confirmation gates). If dates aren't known yet, skip and offer to revisit once the plan has dates set.

## Email

Use when connected to surface booking confirmations missing from the plan. See `references/email-integration.md` for full guidance.
