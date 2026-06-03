# Running With No Connectors

The travel plan is a generated artifact and the source of truth — it always exists, with or without connected tools. When nothing is connected, there's simply nothing to sync to: the plan is the complete, usable record on its own. Offer the connect-to-save benefit **once** per capability, then stop nudging.

The markdown artifact is always generated regardless of connectors — see `itinerary-integration.md`.

## Tasks

Tasks live in the plan. With no task app connected, keep them in the plan artifact as a checklist — checkboxes with a due date in parentheses where the task has a natural deadline. Confirm Claude-initiated additions with the user unless they directed it.

Offer once, e.g.: "I'll keep your tasks in the plan for now. Connect a task app like Todoist and I'll sync them there too."

## Dates and reminders

With no calendar connected, dated items live in the plan — record the trip span and key dated events (flights, check-ins, timed bookings) in a short "Key dates" section near the top so they're easy to scan.

For reminders, use whichever is available in order of preference: task app → scheduled-task capability → skip if neither available. Only set reminders the user confirms. If no reminder capability is available, keep the dated items in the plan and note that reminders would need a connected calendar or task app.

Offer once, e.g.: "No calendar connected, so I've listed the key dates in your plan. Want me to set reminders for the time-sensitive ones?"
