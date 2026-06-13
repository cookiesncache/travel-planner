# Capabilities Reference

Everything Claude can use during a session. Check what's available before proceeding.

If multiple tools of the same type are connected, ask the user which one to sync to for this trip, and record the choice in the state file (see `sync-protocol.md`).

## Itinerary

Any tool that can create and maintain a structured trip plan (e.g. Wanderlog, Notion, Google Docs). Export the plan there; import any changes back. See `itinerary-integration.md` for full guidance.

## Calendar

Any tool that can create and read calendar events (e.g. Google Calendar, Outlook, Apple Calendar). Export the plan's dated items as events; import existing trip events back. See `calendar-integration.md` for full guidance.

*Also used for reminders — see `reminder-integration.md`.*

## Task management

Any tool that can create, read, and update tasks or projects (e.g. Todoist, Asana, Things, Apple Reminders). Export the plan's tasks; import existing tasks back. See `task-integration.md` for full guidance.

*Also used for reminders — see `reminder-integration.md`.*

## Email

Any tool that can search and read emails (e.g. Gmail, Outlook). Use when connected to surface booking confirmations missing from the plan. See `email-integration.md` for full guidance.

## Reminders

Set reminders for time-sensitive prep tasks. Options: calendar alert, due-dated task in the task app, or scheduled-task session capability. If more than one of these is available, ask the user which to use for reminders rather than choosing for them. See `reminder-integration.md` for full guidance.
