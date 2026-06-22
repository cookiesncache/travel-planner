# Sync Protocol

Canonical reference for keeping the travel plan (the source of truth) and connectors in sync. The workflow steps and integration references point here; the rules live here and nowhere else.

## The Two Confirmation Gates

Both gates apply to changes **Claude initiates**. When the user directs an action, act on it directly — do not re-confirm what was just instructed.

- **Gate 1 — plan writes.** Confirm before updating the travel plan, including data imported from connected tools or email.
- **Gate 2 — connector exports.** Before exporting plan data to any connector, get the user's confirmation through a **native `AskUserQuestion` prompt** naming exactly what will be created or changed and in which app; for a batch, list all items in one prompt and export only the ones the user selects.

**Recording exemption (gate 1):** the plan write that records an export carries the authorization of the export it records. After a confirmed export, update Sync State and the affected plan sections immediately — never ask again for that.

Sync-back recording is enforced by the Stop hook (below). **Gate 2 is confirmed in the main thread via `AskUserQuestion`, not a hook** — a prior PreToolUse export-gate hook returned `ask`, but in Cowork that `ask` did not reliably render a native prompt (it intermittently surfaced as a hook error and blocked the write, worst for batched reminders), so consent moved to `AskUserQuestion`, which renders reliably and confirms a whole batch in one prompt. Gate 1 is also prose-only: hooking local file edits would run a check on every Write/Edit in every session, travel or not.

## Hooks — how to cooperate

The plugin ships **one hook** — the **Sync-back check** (Stop): it blocks ending the turn while connector writes or approved imports are not yet recorded in the plan file's ## Sync State, and is the sole enforcer of sync-debt (recording earlier writes before finishing).

**Gate 2 is your job in the main thread, not the hook's.** Before any connector export, present a native `AskUserQuestion` naming exactly what you'll create or change and in which app — one prompt per batch, and the user selects which items to export. Export only what they approve, then record the result in Sync State. A user who directed the action in their own words has already consented — act directly.

How to cooperate:

- **Before a connector write** → confirm via `AskUserQuestion` (above), unless the user already directed it.
- **Sync-back block** → record the writes in Sync State (and update the plan body / `## Bookings` and the spending file), then finish.

The Stop hook only sees MCP tool calls, and gate 2 is prose-driven regardless — so writes made another way (controlling an app's screen, a browser, or a shell) follow the same confirm-first rule in full.

**Connector writes happen in the main thread only.** Subagents are read-only with respect to connectors: they read the plan, search, and report, but never call a connector write tool — the main thread performs every export and records it. This is deliberate — the Stop hook operates on the main agent's turn and gate-2 confirmation happens in the main thread, so a connector write made inside a subagent would bypass both. A discovery agent that surfaces bookings or tasks (e.g. `booking-intel`, `activity-discovery`, `trip-readiness`) returns them as data; the main thread does the writing and the recording.

## Sync State section

Every plan file ends with a `## Sync State` section: one table, one row per (item, connector) pair.

```markdown
## Sync State
<!-- Sync ledger: one row per item-connector pair. Never delete rows; update Status. -->

| ID | Item | Connector | Remote ID | Last action | Status |
|---|---|---|---|---|---|
| tyo-bk1 | Flight JAL 123 (Sep 12) | Google Calendar | evt_8f3k2 | exported 2026-06-10 | synced |
| tyo-tk1 | Apply for visa | Todoist | 7788991122 | imported 2026-06-10 | synced |
| tyo-tk2 | Book airport transfer | Todoist | — | confirmed for export | pending |
| tyo-bk4 | Robot Restaurant tour | — | — | declined by user 2026-06-08 | declined |
| tyo-tk3 | Buy JR Pass | Todoist | 7788991155 | declined by user 2026-06-09 | declined |
```

(`tyo-bk4` was surfaced from email, so it has no remote ID; `tyo-tk3` was surfaced from Todoist, so its app name and remote ID are kept — that ID is what suppresses it next session.)

- **Connector** is the human app name (Google Calendar, Todoist) — never the `mcp__<server>__` segment of a tool name; server names can be opaque and session-specific.
- **Status** is one of: `synced` (plan and connector agree) · `pending` (approved but not yet exported — or an export that was deferred or failed before returning a remote ID) · `stale` (remote change detected, not yet reconciled into the plan body) · `declined` (user rejected the item — never re-surface or export) · `export-declined` (item stays in the plan but the user declined to export it to *this* connector at the gate-2 prompt — kept per (item, connector) so reconcile won't re-offer that export; the item is still live elsewhere) · `untracked` (item lives in a connector but the user declined recording it in the plan — kept only so reconciliation won't re-surface it) · `needs-attention` (problem item, e.g. payment rejected — see `email-integration.md`) · `cancelled` (the booking/item was cancelled at the source — a cancellation email or a user cancellation; no longer happening) · `orphaned` (a once-`synced` row whose remote item no longer exists in its connector — detected during reconcile; surface to the user, don't assume).

## Item IDs

`<tripcode>-<type><n>` — e.g. `tyo-bk1`, `tyo-tk3`, `tyo-rm1`. The trip code is a short lowercase slug chosen when the plan is created and recorded in the state file. Types: `bk` (bookings and itinerary items, including the trip calendar block), `tk` (tasks), `rm` (reminders). IDs are assigned when an item first enters the plan and are never reused or renumbered. Stamp the ID inline next to the item in the plan body (e.g. ``09:00 Flight JAL 123 `tyo-bk1` ``) so body and ledger stay joinable.

## Recording rules

- **Export:** after the connector call(s), add or update one row per item per connector with the remote ID the connector returned, Last action `exported <date>`, Status `synced`. An export is not complete until its row exists — this is the invariant the sync-back hook checks.
- **Pending (deferred or failed export):** if the user approves an export but it is deferred ("push it once the dates firm up") or a connector call fails before returning a remote ID, write the row now with Remote ID `—`, Last action `confirmed for export <date>` (or `export failed <date>`), Status `pending`. When the export later succeeds, update the same row to the returned remote ID, Last action `exported <date>`, Status `synced`. A `pending` row does **not** authorize a silent export later: one carried over from a previous session must be re-confirmed with the user before the call, since the export gate cannot see a past session's approval.
- **Batches:** one user approval covers the whole batch it describes; one Sync State update after the batch is correct — do not interleave a plan write between every call.
- **Import:** assign a new ID, add the item to the plan body, add a row with the source connector and remote ID, Last action `imported <date>`, Status `synced`.
- **Status change** (completion pushed or pulled, remote edit reconciled): update Last action; Status stays `synced`. If a remote change is detected but not yet reconciled into the plan body, set `stale` until it is.
- **Decline:** when the user says no to a surfaced booking or task, add a row with Last action `declined by user <date>`, Status `declined`. **Record the source Connector and Remote ID if the item came from a connector** (a declined Todoist task or calendar event keeps its app name and remote ID) — that ID is the suppression key. Use Connector/Remote ID `—` only for email- or user-surfaced items that have no remote ID. If a decline happens during first-time intake **before the plan file exists**, remember it and write its declined row when the plan file is created (Step 2). Before surfacing anything from email or a connector, check Sync State: a declined row suppresses it permanently unless the user asks.
- **Export declined (gate-2 partial selection):** when the user deselects an item at the gate-2 `AskUserQuestion` export prompt — keeping it in the plan but choosing not to export it to that connector — add or update a row for that (item, connector) with Last action `export declined by user <date>`, Status `export-declined`, Remote ID `—`. This is **not** a full `declined` (the item stays live in the plan and may still export to other connectors). Before re-offering an export, check Sync State: an `export-declined` row for that (item, connector) suppresses re-offering *that* export until the user asks — so a returning trip with a partial export isn't re-proposed item by item every session.
- **Recording declined (untracked):** if the user accepts an item in a connector but declines having it recorded in the plan ("don't bother tracking that here"), still add a minimal row — item, connector, remote ID, Last action `not tracked per user <date>`, Status `untracked` — with no `## Bookings` / spending-file row and no day-by-day detail. This honors the request (no itinerary clutter, no spend row) while giving reconciliation the remote ID it needs so the item isn't re-surfaced as new next session.
- **Reminders:** a reminder set in a connected app (calendar alert or task-app due-date) gets an `rm` Sync State row like any export. A reminder set via the in-session scheduled-task capability is **not** a connector item — note it in the plan body, not the ledger.
- **Cancellation & orphan (subtractive reconcile):** reconciliation runs in the **main thread**, not an agent. (a) When the `booking-intel` agent reports a `cancelled` item — or the user cancels one — set its row to Status `cancelled` and update Last action. (b) During Step 1 reconcile, check whether each `synced` row's remote item still exists in its connector — but **only treat it as `orphaned` when the check is conclusive**: a direct fetch of that remote ID returns not-found, or a *complete, unfiltered* listing of the scope it lives in omits it. A partial / scoped / paginated / date-windowed read, a tool error, multiple calendars, or a task merely filtered out because it's closed is **not** evidence of deletion — never orphan on it (fetch completed tasks before judging a task row — see `task-integration.md`). In both cases **surface the change and get the user's confirmation before editing the plan body** (gate 1): remove or flag the item, update the spending file (drop or relabel the row; totals recalc automatically) and refresh the `## Spending` summary, and make any connector cleanup (deleting a leftover calendar event, closing a task) after gate-2 confirmation (`AskUserQuestion`). If that cleanup is approved but the `ask` is denied or the call fails, keep the row and set Last action `cleanup pending <date>` (Status stays `cancelled`/`orphaned`). **Step 1 reconcile must scan for rows whose Last action is `cleanup pending`, regardless of Status, and re-offer the cleanup through the gate**, clearing the marker once the remote item is confirmed deleted — otherwise the leftover lingers and plan and connector stay divergent. (c) While checking existence, also compare each `synced` row's remote item's key fields (date/time, title) against the plan body; on a mismatch set the row `stale` and surface it for gate-1 reconcile into the plan — this Step-1 compare is the only path that produces `stale`. Never drop a row — re-status it (rows are never deleted).
- **Dedup on import — match the right identifier.** A **connector** item (calendar event, task) carries a remote ID, so an item whose remote ID already appears in Sync State is already handled. An **email** confirmation has a *confirmation number*, not a remote ID — Sync State's Remote ID column holds connector IDs, a different identifier space — so match its confirmation number against the plan's **`## Bookings`** list (`Confirmation #`), not the Remote ID column. Either way: if the match is a `declined`, `untracked`, `cancelled`, or `orphaned` row/item, suppress it (do not re-surface as new); otherwise reconcile its status. Suppression is keyed to the **same booking identity** — the same confirmation number / remote ID, or, for items with no stored number (e.g. `untracked`), the same vendor + dates. A **new** confirmation number for the same vendor + dates of a `cancelled`/`orphaned`/`declined` item is a *re-booking*, not a duplicate — surface it (the old row stays as history).

## Spending file interaction

The money lives in the standalone spending file (`<dest>-spending.xlsx`); the plan keeps only the `## Bookings` identity list and the one-line `## Spending` summary (see `itinerary-integration.md` and `spending-integration.md`). The spending file's first column is the item ID, joined to `## Bookings` and Sync State. Capturing a confirmed booking writes the plan body, the `## Bookings` row, the spending-file row, and the Sync State row in one authorized write, then refreshes the `## Spending` summary. Declined, untracked, and needs-attention items never get a `## Bookings` or spending-file row. **Removing a row on cancel/orphan is item-level, not row-level:** drop the `## Bookings` + spending-file row (totals recalc automatically) only when the *item* is truly gone — every connector row for that ID is `cancelled`/`orphaned` and it's removed from the plan body. An orphan on just one of several connector rows (e.g. the Notion copy deleted while the calendar event still stands) is a connector-cleanup matter, not a spend change — keep the rows. **Non-refundable exception:** when a truly-gone booking leaves a standing non-refundable charge, keep its rows, relabel the Item (e.g. "Hotel Shinjuku (cancelled, non-refundable)"), and set its spending-file Amount to the forfeited amount so it still counts toward the total; only a fully-refunded cancellation drops the rows.

## The state file

`.claude/travel-planner.local.md` in the project directory marks travel planning active and locates the plan across sessions:

```markdown
---
plugin: travel-planner
active_trip: tokyo-2026-09
trips:
  - id: tokyo-2026-09
    trip_code: tyo
    plan_file: tokyo-itinerary.md
    spending_file: tokyo-spending.xlsx
    status: planning      # planning | in-trip | done
    connectors:
      calendar: Google Calendar
      tasks: Todoist
      # budget: Splitwise   # set only when a budget connector is connected; then it
      #                     # becomes the money source of truth and the local file is suppressed
  - id: lisbon-2026-07
    trip_code: lis
    plan_file: lisbon-itinerary.md
    status: done
    connectors:
      calendar: Google Calendar
updated: 2026-06-13
---
```

- **Write it** (ordinary Write tool) as soon as a trip is identified in intake — at the latest when the plan file is created. **Update it** when a plan filename, spending-file name, trip status, or connector choice changes; set a trip's `status: done` when its Follow-up wraps up. Record the user's app choice under that trip's `connectors` when they pick one — that name is what Sync State's Connector column uses.
- **One entry per trip — never overwrite or delete entries.** Starting a new trip *appends* a new entry and repoints `active_trip`; it does not replace the previous trip, whose entry stays so its plan file remains discoverable. `active_trip` is the trip the current session is working on, and the default when the user doesn't say which.
- **It doubles as the returning-user pointer:** Step 1 reads the `trips` list to find each trip's plan file instead of guessing.
- Users should gitignore `*.local.md` (README note).

## After compaction

If context was compacted or history looks truncated, re-read the state file and the plan file **before any connector write**. Sync State on disk outranks your memory of the session: recorded remote IDs prevent duplicate re-exports, and missing confirmations must be re-asked, not assumed.
