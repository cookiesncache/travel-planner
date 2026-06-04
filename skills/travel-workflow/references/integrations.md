# Integrations Reference

Connected tools are bidirectional sync targets for the travel plan — never the source of truth. The plan is the source of truth (see `itinerary-integration.md`). Export plan data to connectors and import their data back into the plan, confirming Claude-initiated plan updates (gate 1) and connector exports (gate 2) with the user.

## Identifying Connected Tools

Check which tools are available by looking at what tools Claude has access to in the current session. Group them by capability:

- **Calendar** — any tool that can create and read calendar events (e.g. Google Calendar, Outlook, Apple Calendar)
- **Itinerary** — any tool that can create and maintain a structured trip plan (e.g. Wanderlog, Notion, Google Docs)
- **Task management** — any tool that can create, read, and update tasks or projects (e.g. Todoist, Asana, Things, Apple Reminders)
- **Email** — any tool that can search and read emails (e.g. Gmail, Outlook)

If multiple tools of the same capability type are connected, ask the user which one to sync to for this trip.

## Calendar

Export the plan's dated items as calendar events; import existing trip events back into the plan. See `calendar-integration.md` for full guidance.

## Itinerary

Export the plan to the connected itinerary app; import any changes back into the plan. See `itinerary-integration.md` for full guidance.

## Task management

Export the plan's tasks to the connected task app; import existing tasks back into the plan. See `task-integration.md` for full guidance.

## Email

Use when connected to surface booking confirmations missing from the plan. See `email-integration.md` for full guidance.
