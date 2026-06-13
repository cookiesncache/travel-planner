# Reminder Integration

Set reminders for time-sensitive prep tasks (e.g. visa application, flight check-in). Only set reminders the user confirms.

## Available reminder capabilities

Check which of the following are available in the current session:

- **Calendar** — create a reminder alert (a calendar event) on the relevant date. This is the one calendar write allowed outside Step 3 itinerary export — see the Step 5 exception in `calendar-integration.md`.
- **Task app** — create a task with a due date in the connected task app
- **Scheduled-task** — the Claude Cowork scheduled task capability; schedules a timed reminder within the session, not a connected app. Check whether scheduled-task tools are available before attempting to use them. This capability is not always present.

## Choosing the capability

These are different capability types, so the "multiple tools of the same type" rule in `capabilities.md` does not settle it — decide as follows:

- **None available** — note in the plan that reminders can't be set, and move on.
- **Exactly one available** — use it.
- **More than one available** — ask the user which they'd like to use for reminders. Do not pick for them based on a default or assumed preference. Record their choice in the state file (a `reminders:` entry under `connectors` — see `sync-protocol.md`) so later sessions don't re-ask.

Record reminders set in a **connected app** (a calendar alert or a task-app due-dated task) in the plan's ## Sync State as an `rm`-type item (see `sync-protocol.md`). **Scheduled-task reminders are exempt:** the in-session scheduled-task capability is not a connected app, so it has no place in the connector ledger — note those in the plan body instead (e.g. a short line under the relevant day), not in ## Sync State.
