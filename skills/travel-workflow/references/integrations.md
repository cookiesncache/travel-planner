# Integrations Reference

## Identifying Connected Tools

Check which tools are available by looking at what tools Claude has access to in the current session. Group them by capability:

- **Calendar** — any tool that can create and read calendar events (e.g. Google Calendar, Outlook, Apple Calendar)
- **Itinerary** — any tool that can create and maintain a structured trip plan (e.g. Wanderlog, Notion, Google Docs)
- **Task management** — any tool that can create, read, and update tasks or projects (e.g. Todoist, Asana, Things, Apple Reminders)
- **Email** — any tool that can search and read emails (e.g. Gmail, Outlook)

If multiple tools of the same capability type are connected, apply capability tiers to select the most capable one. For itinerary tools, use the tiers defined in SKILL.md Step 1. For other capability types, ask the user which tool to use for this trip.

## Session Capabilities

In addition to connected tools, check for session-level capabilities that may be available regardless of connectors:

- **Scheduled-task** — the ability to schedule a timed reminder within the session (not a connected app). Check whether scheduled-task tools are available before attempting to use them. This capability is not always present and should be treated as a last-resort fallback for reminders when no calendar or task app is connected.

## Calendar

Use when connected to create structure around the trip dates.

**Trip event:**
- Create a single event spanning the full trip (departure to return) — use specific times if known, otherwise all-day
- Title: destination(s) — e.g. "Tokyo & Kyoto Trip"

**Individual events to create:**
- Flights (departure time, airline/flight number in description, arrival airport in location)
- Hotel check-ins and check-outs
- Timed-entry bookings (museums, parks, tours)
- Major planned activities with known times

**Reminders:**
- Offer to add reminders for time-sensitive prep tasks — e.g. "Apply for visa" 6 weeks out, "Check in for flight" day before. Use whichever is available: calendar, task app, or scheduled-task capability. Only skip if none are available.

Only create events the user confirms. If dates aren't known yet, skip and offer to revisit once the itinerary has dates set.

## Email

Use when connected to cross-reference existing booking confirmations.

**Search for:**
- Flight confirmations
- Hotel reservations
- Rental car bookings
- Tour or attraction tickets

**For each confirmation found:**
- See `references/email-integration.md` for full cross-referencing and deduplication guidance.
- If not captured anywhere, surface it to the user and offer to add it to the itinerary and/or calendar as appropriate (including confirmation number) — also add a corresponding task if a task tool is connected
- Treat a confirmation email as confirmed. Flag anything that looks structurally incomplete (e.g. missing return leg, no confirmation number). If payment appears rejected or declined, attempt to identify the corresponding booking already captured in context and offer to remove it. If no clear match can be derived, ask the user before taking any action.

Do not read or summarize full email content — only extract booking type, vendor, date(s), and confirmation number where available.
