# Email Integration

Only use this if an email app is connected. Email booking discovery is handled by the **`booking-intel` agent** (read-only) — it scans the inbox and returns a structured digest; this file describes that digest and how the **main thread** acts on it. The agent never writes; the main thread proposes, the user confirms (gate 1), and all writes/exports go through the usual gates.

## The agent's digest

`booking-intel` returns three lists, cross-referenced against the plan (email confirmations deduped by confirmation number against the plan's Bookings / Spending Tracker — not Sync State Remote IDs; `declined`/`untracked`/`cancelled`/`orphaned` items skipped):

- `missing` — valid confirmations not yet in the plan.
- `flagged` — structurally incomplete (missing return leg, no confirmation number) or payment-rejected.
- `cancelled` — cancellations or material changes to items in the plan.

It extracts only booking type, vendor, date(s), confirmation number, and a light source reference — never full email bodies. See `sync-protocol.md` for statuses.

## Handling each result (main thread)

- **`missing` — valid confirmation:** offer to add it to the plan (gate 1; user-directed additions act directly). Once captured, add its Spending Tracker row and Sync State row in the same write (use the confirmation amount if present; otherwise the unknown-amount handling in `itinerary-integration.md`). If the user declines, record a `declined` row so it's never re-surfaced. If the confirmation fulfills an open task (e.g. a flight fulfills "Book flights"), follow the completion-sync rule in `task-integration.md` — ask, then call the app's completion action.
- **`flagged` — structurally incomplete:** flag the gap before adding; do not add silently.
- **`flagged` — payment rejected:** confirm with the user, then flag the corresponding plan item `needs-attention` and create a task to resolve it; do not add as a confirmed booking and do not add a Spending Tracker row. If no matching item is found, surface it and ask whether to add a placeholder task to investigate.
- **`cancelled`:** surface it and confirm before changing anything. **If it has no matching plan item (empty `planItem`)** — e.g. booked-and-cancelled entirely outside the workflow, or a previously `declined` item — treat it as informational: tell the user and change nothing in the plan, Tracker, or connectors (optionally, only on the user's ask, seed a `cancelled` row to suppress future surfacing). **If it matches a plan item**, set that item's Sync State row to `cancelled`, remove or flag it in the plan body, recalculate the Spending Tracker, and make any connector cleanup (delete the leftover calendar event, close the task) after gate-2 confirmation. See the **Cancellation & orphan** rule in `sync-protocol.md`.

All of the above is additive/subtractive *email* reconciliation. The matching *connector-side* subtractive check (a `synced` row whose remote item was deleted → `orphaned`) is done by the main thread during Step 1 reconcile — also per `sync-protocol.md`.
